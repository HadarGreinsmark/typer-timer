import St from 'gi://St';
import Clutter from 'gi://Clutter';
import { Extension } from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import GLib from 'gi://GLib';


export default class TyperTimerExtension extends Extension {
    enable() {
        log("Initializing the extension");
        // Create a Button with initial text
        this._panelButton = new St.Bin({
            style_class: "panel-button",
        });
        let panelButtonText = new St.Label({
            text: "Loading...",
            y_align: Clutter.ActorAlign.CENTER,
        });
        this._panelButton.set_child(panelButtonText);


        let decoder = new TextDecoder();

        // Read and update the text every second
        GLib.timeout_add_seconds(GLib.PRIORITY_DEFAULT, 5, () => {
            let [success, contents] = GLib.file_get_contents("/tmp/typer-timer/banner");
            let contents_str = decoder.decode(contents)
            if (success) {
                panelButtonText.set_text(contents_str);
            }
            return true;
        });

        // Add the button to the panel
        Main.panel._rightBox.insert_child_at_index(this._panelButton, 0);
    }

    disable() {
        // Remove the added button from panel
        Main.panel._rightBox.remove_child(this._panelButton);
        this._panelButton?.destroy();
        this._panelButton = null;
    }
}
