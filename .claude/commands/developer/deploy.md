Deploy the StreamTeX project to the specified target.

Arguments: $ARGUMENTS (target: "docker", "huggingface", or "gcp")

## Pre-Deployment Checks (all targets)

1. **Read configuration**: Read `Dockerfile`, `pyproject.toml`, and the active project's `.streamlit/config.toml`.
2. **Run tests**: Execute `uv run pytest tests/ -v` and abort if any fail.
3. **Verify requirements**:
   - `streamlit>=1.54.0` is in `pyproject.toml` dependencies
   - `.streamlit/config.toml` has `enableStaticServing = true`
   - All image assets referenced in blocks exist in `static/images/`
4. **Check git status**: Ensure all changes are committed (warn if uncommitted changes exist).

## Target: docker

Build and run locally in Docker:
```bash
# Replace <your_project> with the actual project path (e.g., projects/my_project)
docker build --build-arg FOLDER=<your_project> -t streamtex-app .
docker run -p 8501:8501 streamtex-app
```
Then verify the app is accessible at `http://localhost:8501`.
Report the health check status.

## Target: huggingface

1. Verify the `Dockerfile` is Hugging Face Spaces compatible:
   - Uses `EXPOSE 8501`
   - Has a health check
   - Entry point runs `streamlit run`
2. Remind the user to:
   - Create a Space on Hugging Face (Docker SDK type)
   - Add the HF Space as a git remote: `git remote add hf https://huggingface.co/spaces/[user]/[space]`
   - Push: `git push hf main`
3. Show the expected Space URL: `https://huggingface.co/spaces/[user]/[space]`

## Target: gcp

1. Check for Ansible inventory file (`inventory.ini`) and playbook (`deploy.yml`).
2. Verify SSH key configuration.
3. Remind the user of the deployment command:
   ```bash
   ansible-playbook -i inventory.ini deploy.yml
   ```
4. After deployment, verify the app is accessible on the GCP VM's IP at port 8501.

## Target: env-sync

Synchronize environment variables from `render.yaml` to live Render services:

```bash
stx deploy env-sync                     # Sync all services
stx deploy env-sync --dry-run           # Show diff without applying
stx deploy env-sync --service svc-name  # Sync one service only
stx deploy env-sync --path ./my-project # Custom project path
```

**Workflow:**
1. Reads `render.yaml` to extract service names and their `envVars`
2. Reads `~/.render/cli.yaml` for the API key (requires `render login`)
3. Resolves service IDs via the Render API
4. For each service: fetches current env vars, computes diff, displays a Rich table
5. If not `--dry-run`: applies changes via `PUT /services/{id}/env-vars`
6. Optionally triggers a redeploy after applying changes

## Post-Deployment

- Report deployment status (success/failure)
- Show the app URL
- Suggest running `/designer:block-preview` on key blocks if visual issues are suspected
