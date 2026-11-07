# Publication guide: TwinPrivacy GitHub repository

This ZIP is a *prepared repository*, not an already published GitHub page.
Publication needs an authenticated GitHub account and a repository owner.

## Before publishing

- Confirm the intended repository owner and scientific authorship.
- Review licence permissions: MIT for code and tests, CC0 1.0 for
  generated data, and CC BY 4.0 for reports and documentation. A licence
  grants public reuse rights. Every file has an SPDX identifier or sidecar.
- Verify that no restricted data, real patient records, credentials, or
  unlicensed third-party content have been included.
- Review the AI-assistance disclosure in `docs/LICENSING_AND_AI_USE.md`.
    - Read the technical limitations and provenance statements before linking
  the repository to a grant application.

## Method A: browser upload

1. Visit https://github.com/new and sign in.
2. Set repository name to `TwinPrivacy` (or a name you prefer).
3. Choose **Public**. Do **not** initialize with a new README, .gitignore,
   or licence: those files are already present in this package.
4. Create the empty repository. On its new page choose **uploading an
   existing file** / **Add file → Upload files**.
5. Extract the ZIP locally. Upload the **contents inside** the `TwinPrivacy`
   folder, preserving subdirectories and the hidden `.github` folder.
   Do **not** upload the ZIP as the sole item.
6. Commit the files to the default branch. Check that folders `data/`,
   `docs/`, `examples/`, `evidence/`, `outputs/`, and `.github/` appear.
7. Visit the **Actions** tab and confirm the workflow `Reproduce and verify`
   runs successfully. GitHub may require initial action approval.
8. Copy the verified public repository URL into the grant application.

Browser uploads are less reliable for whole directory trees and hidden
files. If your browser omits `.github/`, use the Git method below.

## Method B: Git command line (recommended)

After you have created an **empty public repository** in GitHub:

```bash
cd TwinPrivacy
python reproduce.py
git init -b main
git add .
git commit -m "Publish TwinPrivacy research software and validation evidence"
git remote add origin https://github.com/YOUR-USERNAME/TwinPrivacy.git
git push -u origin main
```

Replace `YOUR-USERNAME` with the username or organization owning the
repository, then authenticate when GitHub prompts you. Never paste access
tokens into files or send them in a chat.

## Checks after publication

- `README.md` renders correctly on the repository homepage.
- `LICENSE` shows MIT; data have CC0 terms; reports have CC BY 4.0 terms.
- Both report files are present:
  `outputs/patient_disclosure_statement.html` and
  `evidence/results/VALIDATION_REPORT.html`.
- The automated GitHub Actions run is green (not yet tested until the
  repository is actually published).
- An independent person can clone the repository and run
  `python reproduce.py` successfully.
- The public URL is reachable without signing in.

Do not claim publication or continuous integration success until the
GitHub repository and workflow are actually live and checked.
