from fastapi import APIRouter
from pydantic import BaseModel
from aiortc import RTCPeerConnection, RTCSessionDescription
import asyncio

from backend.realtime.audio_stream.pipeline import AudioPipeline
from backend.realtime.webrtc.audio_track import (
    IncomingAudioSink,
    OutgoingAudioTrack
)

router = APIRouter()
pcs = {}  # Changed to dict to track pipelines

class Offer(BaseModel):
    sdp: str
    type: str

async def cleanup_pc(pc_id, pc):
    """Cleanup peer connection and remove from dict"""
    await asyncio.sleep(0.1)
    if pc_id in pcs:
        del pcs[pc_id]
    try:
        await pc.close()
    except:
        pass
    print(f"[WebRTC] Peer connection {pc_id} closed. Active connections: {len(pcs)}")

@router.post("/webrtc/offer")
async def webrtc_offer(offer: Offer):
    import uuid
    pc_id = str(uuid.uuid4())[:8]
    
    print(f"[WebRTC] Received offer {pc_id}. Active connections: {len(pcs)}")
    
    pc = RTCPeerConnection()
    pipeline = AudioPipeline()
    audio_sink = None
    outgoing_track = None
    
    # Store in dict
    pcs[pc_id] = {
        "pc": pc,
        "pipeline": pipeline
    }

    @pc.on("track")
    def on_track(track):
        nonlocal audio_sink, outgoing_track
        print(f"[WebRTC {pc_id}] Track received: {track.kind}")
        
        if track.kind == "audio":
            # Create incoming audio sink
            audio_sink = IncomingAudioSink(track, pipeline)
            
            # Create and add outgoing track
            outgoing_track = OutgoingAudioTrack(pipeline)
            pc.addTrack(outgoing_track)
            
            print(f"[WebRTC {pc_id}] Audio tracks connected")
            
            # Handle track ending
            @track.on("ended")
            async def on_ended():
                print(f"[WebRTC {pc_id}] Incoming track ended")
                if audio_sink:
                    audio_sink.stop()

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        state = pc.connectionState
        print(f"[WebRTC {pc_id}] Connection state: {state}")
        
        if state == "connected":
            print(f"[WebRTC {pc_id}] Connection established successfully")
        elif state in ["failed", "closed"]:
            print(f"[WebRTC {pc_id}] Connection terminated")
            if audio_sink:
                audio_sink.stop()
            await cleanup_pc(pc_id, pc)

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        state = pc.iceConnectionState
        print(f"[WebRTC {pc_id}] ICE state: {state}")
        
        if state == "failed":
            print(f"[WebRTC {pc_id}] ICE connection failed")
            await pc.close()

    try:
        # Set remote description
        await pc.setRemoteDescription(
            RTCSessionDescription(
                sdp=offer.sdp,
                type=offer.type
            )
        )

        # Create answer
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        print(f"[WebRTC {pc_id}] Answer created successfully")

        return {
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        }
    
    except Exception as e:
        print(f"[WebRTC {pc_id}] Error creating answer: {e}")
        import traceback
        traceback.print_exc()
        
        if pc_id in pcs:
            del pcs[pc_id]
        await pc.close()
        raise

@router.on_event("shutdown")
async def shutdown():
    """Cleanup all peer connections on shutdown"""
    print("[WebRTC] Shutting down, closing all connections")
    coros = [data["pc"].close() for data in pcs.values()]
    await asyncio.gather(*coros, return_exceptions=True)
    pcs.clear()