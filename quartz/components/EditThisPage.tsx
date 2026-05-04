import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { classNames } from "../util/lang"

interface EditThisPageOptions {
  // GitHub repo in "owner/name" form
  repo: string
  // Default branch (usually main or v4)
  branch: string
  // Path inside the repo to the content folder (relative to repo root)
  contentPath: string
}

export default ((opts: EditThisPageOptions) => {
  const EditThisPage: QuartzComponent = ({ fileData, displayClass }: QuartzComponentProps) => {
    const rel = fileData.relativePath
    if (!rel) return null
    const encoded = rel
      .split("/")
      .map((seg) => encodeURIComponent(seg))
      .join("/")
    const url = `https://github.com/${opts.repo}/edit/${opts.branch}/${opts.contentPath}/${encoded}`
    return (
      <div class={classNames(displayClass, "edit-this-page")}>
        <a href={url} target="_blank" rel="noopener noreferrer">
          edit this page on github →
        </a>
      </div>
    )
  }

  EditThisPage.css = `
    .edit-this-page {
      margin-top: 1.5rem;
      font-size: 0.85rem;
      opacity: 0.6;
      transition: opacity 0.2s ease;
    }
    .edit-this-page:hover {
      opacity: 1;
    }
    .edit-this-page a {
      color: var(--gray);
      text-decoration: none;
    }
    .edit-this-page a:hover {
      color: var(--secondary);
    }
  `

  return EditThisPage
}) satisfies QuartzComponentConstructor<EditThisPageOptions>
