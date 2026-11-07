---
title: How to Write a Notes File
subtitle: Every marker the notebook understands, on three pages
kicker: format guide
tagline: Write plain Markdown, add a few markers, run the notebook, get a handwritten PDF.
cover_icons: [pencil, book, star, bolt, sheet, rocket]
chips: [Markdown in, PDF out, zero layout code]
footer: One Markdown file in, one notebook PDF out.
---

<!-- section: The basics -->
# Pages, Headings & Text
<!-- sub: Every line starting with one # begins a new page. The line below the title can be a subtitle. -->

Every line starting with `# ` begins a **new page** with a numbered, colourful title. Put `<!-- sub: your subtitle -->` right under it for the small line beneath the title. Everything until the next `#` belongs to that page.

## Headings cycle through four inks
Use `##` for sections and `###` for small headings.

## Inline shortcuts
| You type | You get |
|---|---|
| `==highlight==` | ==highlighter pen== |
| `[[Ctrl]] [[Enter]]` | [[Ctrl]] [[Enter]] |
| `{r:red ink}` `{b:blue}` `{t:teal}` `{g:green}` `{p:purple}` `{a:amber}` `{k:pink}` | {r:red ink} {b:blue} {t:teal} {g:green} {p:purple} {a:amber} {k:pink} |
| `:bulb: :robot: :mail:` | :bulb: :robot: :mail: |
| `**bold**` / `*light*` | **bold** / *light* |
| `` `code` `` | `code` |
| `((Anna 13.39))` `((r:red))` `((b:blue))` | ((Anna 13.39)) ((r:red)) ((b:blue)) |

- [x] task lists with `- [x]`
- [ ] and `- [ ]`

> tip: Callouts start with a keyword: `tip`, `note`, `warning`, `example`, `info`, `remember`, `ai`, `cost`, `pro`, `try`, `plain`.

> warning "Custom title": Add a title in quotes before the colon.

> takeaway: `> takeaway:` draws the cloud. `> footer:` replaces the footer banner on that page.

# Layout Blocks
<!-- sub: Columns, boxes, stickies, steps and flow diagrams. -->

:::: cols
**`::: cols`** splits into columns. Put `---` between columns.

---
> sticky "Sticky note": `> sticky:` or `::: sticky "Title"` makes one, colours rotate.

---
::: box blue "Box with title" :star:
`::: box colour "Title" :icon:` with colours ink, blue, teal, red, green, purple, amber, pink. Add `dash` for dashes or `nofill` for no tint.
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

:::: grid 3
::: box teal "grid 3"
`::: grid 3` makes equal cards. Put one `::: box` per card.
:::
::: box purple "No colour?"
A `::: box` without a colour gets one automatically.
:::
::: box amber "Nesting"
You may get the colon counts wrong. The notebook fixes nesting for you.
:::
::::

> takeaway: Use `<!-- section: Name -->` before a page to group the contents list and set the part label above the title.

<!-- section: Colour, results & diagrams -->
# Colour, Results & Diagrams
<!-- sub: The markers that give the notes their Method 1 look. -->

## Code gets coloured ink
Fence code with a language: `sql`, `dax`, `python`, `js`. Keywords turn blue, functions teal, text values green, table names orange and comments grey.

```sql
-- cheap dairy products
SELECT product_name, price
FROM products
WHERE category = 'Dairy' AND price < 2;
```

> plain: show the name and price of dairy products under 2 euros. `> plain:` adds the purple "In plain English" line under every query.

## Show real results
Use a small table for rows, or chips for short lists: ((Whole Milk 1.10)) ((Greek Yogurt 0.79)). Chips take a colour letter: `((g:ok))` `((r:error))`.

:::: cols
## Labelled parts
::: parts
SELECT | keyword\n"show me" | blue
price | column | ink
FROM | keyword | blue
products | table | red
;  | stop | pink
:::

Each line is `text | caption | colour`. Use `\n` for a line break in the caption.

---

## Stage boxes
::: chain
(blue) FROM :: find the table
(red) WHERE :: drop rows
(green) SELECT :: pick columns
:::

`::: chain` joins boxes with arrows. Optional `(colour)` prefix, `::` splits title and small text. `::: chain v` makes a numbered vertical list.
::::

::: box green "Automatic colour" :sparkle:
With `AUTO_COLOUR = True` in the settings, plain Markdown still gets colour: tinted table headers, coloured first columns, rotating bullet colours, tinted headings and untagged code that looks like SQL or DAX. Boxes, callouts and code fills come from `FILL_BOXES`.
:::

> takeaway: For the richest pages: coloured boxes, `> plain:` lines, ((chips)) or tables for every result, a fenced `sql` block for every query, and a `> takeaway:` on every page.
