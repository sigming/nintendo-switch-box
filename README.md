<p align="center">
  <a href="https://gist.github.com/Swilder-M/4aa566c004d4baac8561a36ae02bc2ea"><img width="400" src="https://raw.githubusercontent.com/Swilder-M/nintendo-switch-box/master/assets/pinned.png"></a>
  <h3 align="center">🎮 nintendo-switch-box</h3>
  <p align="center">Update a pinned gist to contain your Nintendo Switch Game stats</p>
</p>

## Setup
1. Fork [this repository](https://github.com/Swilder-M/nintendo-switch-box).

2. Create a new **public** GitHub Gist at <https://gist.github.com/>.

3. Go to <https://github.com/settings/tokens/new> to create a token with only the **gist** permission.

4. Run `python src/get_session_token.py` to obtain your session token.

5. Go to your fork's **Settings > Secrets** and add the following environment variables:
   - `NINTENDO_SESSION_TOKEN`: The session token obtained in the previous step.
   - `GH_TOKEN`: The token created in step 3.
   - `GIST_ID`: The ID portion of your gist URL: `https://gist.github.com/your_name/<GIST_ID>`.
