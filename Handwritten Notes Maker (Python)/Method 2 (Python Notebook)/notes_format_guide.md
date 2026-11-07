---
title: How to Write a Notes File
subtitle: Every marker the notebook understands, on two pages
kicker: format guide
tagline: Write plain Markdown, add a few markers, run the notebook, get a handwritten PDF.
cover_icons: [pencil, book, star, bolt, sheet, rocket]
chips: [Markdown in, PDF out, zero layout code]
footer: One Markdown file in, one notebook PDF out.
---

<!-- section: The basics -->
# Pages, Headings & Text

Every line starting with `# ` begins a **new page** with the boxed title. Everything until the next `#` belongs to that page.

## Headings cycle through four inks
Use `##` for sections and `###` for small headings.

## Inline shortcuts
| You type | You get |
|---|---|
| `==highlight==` | ==highlighter pen== |
| `[[Ctrl]] [[Enter]]` | [[Ctrl]] [[Enter]] |
| `{r:red ink}` `{b:blue}` `{t:teal}` `{g:green}` `{p:purple}` `{a:amber}` | {r:red ink} {b:blue} {t:teal} {g:green} {p:purple} {a:amber} |
| `:bulb: :robot: :mail:` | :bulb: :robot: :mail: |
| `**bold**` / `*light*` | **bold** / *light* |
| `` `code` `` | `code` |

- [x] task lists with `- [x]`
- [ ] and `- [ ]`

> tip: Callouts start with a keyword: `tip`, `note`, `warning`, `example`, `info`, `remember`, `ai`, `cost`, `pro`, `try`.

> warning "Custom title": Add a title in quotes before the colon.

> takeaway: `> takeaway:` draws the cloud. `> footer:` replaces the footer banner on that page.

# Layout Blocks

:::: cols
**`::: cols`** splits into columns. Put `---` between columns.

---
> sticky "Sticky note": `> sticky:` or `::: sticky "Title"` makes one, colours rotate.

---
::: box blue "Box with title" :star:
`::: box colour "Title" :icon:` with colours ink, blue, teal, red, green, purple, amber. Add `dash` for dashes.
:::
::::

::: steps
1. **Write** the `.md` file
2. **Run** all cells
3. **Read** the PDF
:::

::: flow How a flow diagram looks
*[clock] Schedule -> [sheet] Read sheet -> [branch] IF -> true: [mail] Email | false: [hash] Slack
:::

Write `::: flow caption`, then lines like `*[clock] Name -> [mail] Name`. `*` marks a trigger, `[icon]` picks the doodle, `a | b` makes branches, `label: ` writes on the arrow.

> takeaway: Use `<!-- section: Name -->` before a page to group the contents list. Nest blocks by giving the outer one four colons (`::::`).
