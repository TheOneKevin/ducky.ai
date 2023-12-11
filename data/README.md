Process:
1. Run `splitter.py` to split the ASCIIdocs and get the token counts
2. Run `count_tokens.py` to validate token counts. Each text fragment must have < 512 tokens. The fragments with > 512 tokens must be either:
    - Validated that we can safely truncate it without much information loss
    - Manually split so the token count < 512
3. Run `gentoc.py` to generate page links against the reference PDF file. A list of cross-referenced headings will be displayed, and headings with no corresponding PDF cross-reference will be shown.
    - Make sure the headings with no corresponding PDF reference are valid.

