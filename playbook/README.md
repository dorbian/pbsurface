# PlayBook native client

This directory is intentionally a hardware-gated scaffold.

The native client will use the BlackBerry Tablet OS 2.1 Native SDK and:

- BPS for lifecycle and navigator events;
- Screen for native surfaces, touch and button rendering;
- `mm-renderer` for RTP/RTSP video and audio;
- POSIX sockets for discovery and control;
- locally bundled assets with no runtime BlackBerry service dependency.

Do not copy archived SDK or firmware files into this repository. Place them in
ignored `toolchains/` and `firmware/` directories or reference an external local
installation. The first source implementation should be based on the preserved
official HelloWorldDisplay, Gesture, VideoPlayback and VideoWindow samples and
accepted on a real device before expanding the architecture.

