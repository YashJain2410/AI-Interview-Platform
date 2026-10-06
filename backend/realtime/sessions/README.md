# Text session state

`SessionManager` creates UUID sessions and stores them in a process dictionary. `models.py` defines stages and message/session models.

Sessions start at `intro`; the current flow does not advance stages or populate the transcript model. Disconnect removes the session. State is not durable or shared across workers. See [architecture](../../../docs/architecture.md#state-and-lifecycle).
