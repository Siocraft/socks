# dat-files

Put **real** sock design `.dat` files here—files that **Winpds already opens** with your usual reader (for example Korea-Robot Drumless / PDS 8F).

The Python tools only require the total size **80,208 bytes** and treat the first **48 bytes** as an opaque header that is **copied unchanged** when writing a new file. Those bytes are **not** arbitrary: Winpds validates pattern head information. A file with a random or synthetic header will fail in Winpds with errors such as **“Korea-Robot is not PDS 8F Pattern.”**

Do not rely on hand-made samples for opening in Winpds; start every workflow from a design saved in Winpds.
