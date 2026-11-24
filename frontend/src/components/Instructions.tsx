export default function Instructions() {
  return (
    <div className="row">
      <div className="col-md-12 mx-auto">
        <h4>How to use AutoChannel?</h4>
        <h3>Login? (skip if already logged in)</h3>
        <ol>
          <li>On the left side click on the user icon</li>
          <li>Accept the discord authorization</li>
        </ol>
        <h3>How to add AutoChannel bot to your server?</h3>
        <ol>
          <li>In the navbar or the server select page, select the server you want to update</li>
          <li>
            If the bot hasn't been added yet, you will be asked to add the bot to your managed
            server through Discord
          </li>
        </ol>
        <h3>What to do after I added the bot to my server?</h3>
        <ol>
          <li>Either click "Dashboard" or click your server icon in the navbar</li>
          <li>In the server category dashboard you can make your desired changes</li>
          <li>
            Options you can modify:
            <ul>
              <li>Enabled: Enables the autochannel to create channels in this category</li>
              <li>
                Prefix: This sets the prefix of each channel created in your designated category.
                Must be unique prefix in that category. This is important as this tells the bot if
                the channel is managed by it or a static channel on the server. (default AC!)
              </li>
              <li>
                Channel size: This sets the size of the channel, which is the number of users who
                can connect to the autocreated channels, 0 means unlimited. (default 10)
              </li>
              <li>
                Empty count: This sets the number of empty channels the category should always
                have. Recommended is the default of 1, but for larger communities having up to 10
                empty channels will make this easier to find spare rooms. (default 1)
              </li>
            </ul>
          </li>
          <li>
            For each text or number setting, press the check mark (or Enter) next to the entry to
            save it. Toggles save immediately. When successful you will see a green notification
            with the updated changes.
          </li>
          <li>
            Final step: as an admin in your server run "!acupdate" for AutoChannel update and it
            will sync the bot with the configurations you just set
          </li>
        </ol>
      </div>
      <div className="col-md-6 mx-auto">
        <img className="img-fluid" width={600} src="/img/autochannel-instructions-2.gif" alt="Dashboard walkthrough" />
      </div>
    </div>
  );
}
