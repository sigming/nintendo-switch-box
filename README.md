<p align="center">
  <a href="https://gist.github.com/sigming/4aa566c004d4baac8561a36ae02bc2ea"><img width="400" src="https://raw.githubusercontent.com/sigming/nintendo-switch-box/master/assets/pinned.png"></a>
  <h3 align="center">🎮 nintendo-switch-box</h3>
  <p align="center">Update a pinned gist to contain your Nintendo Switch Game stats</p>
</p>

## Setup

You don't need to fork this repository. Create your own repository and add a workflow that uses this action.

1. Create a new repository (public or private) to run the action. It stores your Nintendo Switch stats and holds the required secrets.

2. Create a new **public** GitHub Gist at <https://gist.github.com/>.

3. Go to <https://github.com/settings/tokens/new> to create a token with only the **gist** permission.

4. Get your Nintendo session token. Clone this repository locally and run the helper script, then follow the prompts:

   ```bash
   git clone https://github.com/sigming/nintendo-switch-box.git
   cd nintendo-switch-box
   uv run python src/get_session_token.py
   ```

5. Go to your repository's **Settings > Secrets and variables > Actions** and add the following secrets:
   - `NINTENDO_SESSION_TOKEN`: The session token obtained in step 4.
   - `GH_TOKEN`: The token created in step 3.
   - `GIST_ID`: The ID portion of your gist URL: `https://gist.github.com/your_name/<GIST_ID>`.

6. Add a workflow file at `.github/workflows/nintendo-switch-box.yml` in your repository:

   ```yaml
   name: Update gist with Nintendo Switch Game stats
   on:
     schedule:
       - cron: "0 23 * * *"
     workflow_dispatch:
   jobs:
     update-gist:
       runs-on: ubuntu-latest
       steps:
         - name: Update gist
           uses: sigming/nintendo-switch-box@v3
           env:
             NINTENDO_SESSION_TOKEN: ${{ secrets.NINTENDO_SESSION_TOKEN }}
             GH_TOKEN: ${{ secrets.GH_TOKEN }}
             GIST_ID: ${{ secrets.GIST_ID }}
   ```

7. Trigger the workflow once from the **Actions** tab (Run workflow), then [pin the gist](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/pinning-items-to-your-profile#pinning-items-to-your-profile) to your profile.
