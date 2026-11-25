export default function Instructions() {
  return (
    <ol className="steps prose">
      <li className="step surface">
        <h2>Log in (skip if already logged in)</h2>
        <ol>
          <li>
            Click <strong>Login</strong> in the top bar
          </li>
          <li>Accept the Discord authorization</li>
        </ol>
      </li>
      <li className="step surface">
        <h2>Add the AutoChannel bot to your server</h2>
        <ol>
          <li>
            Open <strong>Servers</strong> and select the server you want to update
          </li>
          <li>
            If the bot hasn't been added yet, you will be asked to add the bot to your managed
            server through Discord
          </li>
        </ol>
      </li>
      <li className="step surface">
        <h2>Choose your settings</h2>
        <p>Each category of your server has its own settings:</p>
        <ul>
          <li>
            <strong>Enabled:</strong> Enables the autochannel to create channels in this category
            (default Off)
          </li>
          <li>
            <strong>Prefix:</strong> This sets the prefix of each channel created in your designated
            category. Must be unique prefix in that category. This is important as this tells the
            bot if the channel is managed by it or a static channel on the server. (default AC!)
          </li>
          <li>
            <strong>Channel size:</strong> This sets the size of the channel, which is the number of
            users who can connect to the autocreated channels, 0 means unlimited. (default 10)
          </li>
          <li>
            <strong>Empty count:</strong> This sets the number of empty channels the category should
            always have. Recommended is the default of 1, but for larger communities having up to 10
            empty channels will make this easier to find spare rooms. (default 1)
          </li>
        </ul>
        <p className="mt-3 mb-0">
          For each text or number setting, press <strong>Save</strong> (or Enter) next to the entry
          to save it. Toggles save immediately. When successful you will see a green notification
          with the updated changes.
        </p>
      </li>
      <li className="step surface">
        <h2>Sync the bot</h2>
        <p className="mb-0">
          As an admin in your server run <code>!acupdate</code> for AutoChannel update and it will
          sync the bot with the configurations you just set.
        </p>
      </li>
      <li className="step surface">
        <h2>See it in action</h2>
        <img
          className="screenshot"
          width={600}
          src="/img/autochannel-instructions-2.gif"
          alt="Dashboard walkthrough"
        />
      </li>
    </ol>
  );
}
