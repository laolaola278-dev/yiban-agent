
# -*- coding: utf-8 -*-
from pypdf import PdfReader
import sys
r = PdfReader(sys.argv[1])
texts = []
for p in r.pages:
    texts.append(p.extract_text() or "")
full = "\n".join(texts)
open(sys.argv[2], "w", encoding="utf-8").write(full)
print("PAGES:", len(r.pages), "LEN:", len(full))
