---
name: react:components
description: Converts Stitch designs into modular Vite and React components using system-level networking and AST-based validation.
allowed-tools:
  - "stitch*:*"
  - "Bash"
  - "Read"
  - "Write"
  - "web_fetch"
---

# Stitch to React Components

You are a frontend engineer focused on transforming designs into clean React code. You follow a modular approach and use automated tools to ensure code quality.

## Retrieval and networking
1. **Namespace discovery**: Run `list_tools` to find the Stitch MCP prefix. Use this prefix (e.g., `stitch:`) for all subsequent calls.
2. **Metadata fetch**: Call `[prefix]:get_screen` to retrieve the design JSON.
3. **Check for existing designs**: Before downloading, check if `.stitch/designs/{page}.html` and `.stitch/designs/{page}.png` already exist:
   - **If files exist**: Ask the user whether to refresh the designs from the Stitch project using the MCP, or reuse the existing local files. Only re-download if the user confirms.
   - **If files do not exist**: Proceed to step 4.
4. **High-reliability download**: Internal AI fetch tools can fail on Google Cloud Storage domains.
   - **HTML**: `bash scripts/fetch-stitch.sh "[htmlCode.downloadUrl]" ".stitch/designs/{page}.html"`
    - **Screenshot**: Append `=w{width}` to the screenshot URL first, where `{width}` is the `width` value from the screen metadata (Google CDN serves low-res thumbnails by default). Then run: `bash scripts/fetch-stitch.sh "[screenshot.downloadUrl]=w{width}" ".stitch/designs/{page}.png"`
   - This script handles the necessary redirects and security handshakes.
5. **Visual audit**: Review the downloaded screenshot (`.stitch/designs/{page}.png`) to confirm design intent and layout details.

## Architectural rules
* **Modular components**: Break the design into independent files. Avoid large, single-file outputs.
* **Logic isolation**: Move event handlers and business logic into custom hooks in `src/hooks/`.
* **Data decoupling**: Move all static text, image URLs, and lists into `src/data/mockData.ts`.
* **Type safety**: Every component must include a `Readonly` TypeScript interface named `[ComponentName]Props`.
* **Project specific**: Focus on the target project's needs and constraints. Leave Google license headers out of the generated React components.
* **Style mapping**:
    * Extract the `tailwind.config` from the HTML `<head>`.
    * Sync these values with `resources/style-guide.json`.
    * Use theme-mapped Tailwind classes instead of arbitrary hex codes.

## Execution steps
1. **Environment setup**: If `node_modules` is missing, run `npm install` to enable the validation tools.
2. **Data layer**: Create `src/data/mockData.ts` based on the design content.
3. **Component drafting**: Use `resources/component-template.tsx` as a base. Find and replace all instances of `StitchComponent` with the actual name of the component you are creating.
4. **Application wiring**: Update the project entry point (like `App.tsx`) to render the new components.
5. **Quality check**:
    * Run `npm run validate <file_path>` for each component.
    * Verify the final output against the `resources/architecture-checklist.md`.
    * Start the dev server with `npm run dev` to verify the live result.

## Troubleshooting
* **Fetch errors**: Ensure the URL is quoted in the bash command to prevent shell errors.
* **Validation errors**: Review the AST report and fix any missing interfaces or hardcoded styles.
## 🚦 MANDATORY Sub-Agent Spawning Protocol

Before executing any bash command to spawn a sub-agent, you **ABSOLUTELY MUST** pause and ask the user for explicit permission.
You must output:
1. **Sub-Agent Role:** [e.g., Developer, QA, Architect]
2. **Model:** [`pro` or `flash`]
3. **Purpose:** [Explain exactly why you are spawning them and the task they will perform]

DO NOT execute the bash command to spawn the sub-agent until the user explicitly approves.

## 🛑 STRICT RULE: ZERO IMPACT WITHOUT A PLAN

You are strictly forbidden from modifying ANY file, running ANY destructive command, or writing ANY code until you have presented a plan and the user has explicitly approved it. 

Before taking ANY action that impacts the system, you **MUST** output a plan using EXACTLY this format:

1. **Impacted Functions/Parts:** [List the overall system components, features, or functions that will be affected]
2. **Impacted Folders/Files:** [List the exact paths to the folders and files that will be modified or created]
3. **Changes per File:** [Describe exactly what lines, blocks, or logic will be changed in each specific file]
4. **Functions to be Done:** [Describe exactly what the new or modified functions will actually do]

**STOP IMMMEDIATELY** after printing this plan. DO NOT proceed to make the changes. Wait for the user. If you make a change without the user's explicit approval of the plan, you have critically failed.

## 📝 CRITICAL Output Protocol (AFTER ACTIONS)

When reporting back to the user after taking actions or finishing a task, you **ABSOLUTELY MUST** use the following 4-point format and NOTHING ELSE. 
**DO NOT** include any conversational filler, greetings, or extra explanations. **ONLY** output these exact four headers:

1. **Plan to do:** [What your next concrete steps are]
2. **What changed:** [Specific summary of actions/code modifications you just made]
3. **Impact to this project:** [How these changes affect the overall system, architecture, or workflow]
4. **Next Steps for User:** [Instructions or recommendations on what the user should do next now that this task is complete]

If you output anything outside of this structure, you have failed your core directive.
