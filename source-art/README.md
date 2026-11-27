# Source artwork

Full-resolution AI-generated originals, exactly as they came out of the
generator. These are **not** served by the website, and they are **not** what
`assets/img/` is built from any more.

Every bottle in them carries garbled label text, for example "Casual In Sexuit
Penfarinione" and "Stemm Mattural Blrength", and a legible "Makes Erection
Strong" claim. None of it is real product copy.

`fixed/` holds the same art with that text rebuilt and reset to three lines that
are true and that come from `assets/js/config.js`. It is generated, not edited
by hand:

```powershell
python tools/fix_labels.py
```

```powershell
python tools/build_images.py
```

`tools/fix_delivery.py` is separate: it reframes the delivery photograph so the
card terminal falls outside the frame, and records in its header why painting
the terminal out was tried and abandoned.

`hero-sprout-source.mp4` is the video the hero clip is cut from. Its second
half carries garbled gold lettering reading "ALL FROM NATURAL ROOTS" and is not
used; `tools/build_hero_video.py` explains why and rebuilds the clip.

Replace all of it with genuine photographs of the real bottle, front and back,
before the site is advertised anywhere.
