import gettext
import subprocess

_ = gettext.gettext


class PathExporterPanelDelegate:

    def __init__(self, api):
        self.api = api
        self.panel_id = "path-exporter"
        self.panel_name = _("Path Exporter")
        self.panel_positions = ["left", "right"]
        self.panel_position = "right"

    def create_panel_widget(self, ui, document_controller):
        main_column = ui.create_column_widget()
        widget = ui.create_push_button_widget('Copy data item paths')

        def copy2clip_unix(txt):
            cmd = 'echo ' + txt.strip() + '|pbcopy'
            return subprocess.check_call(cmd, shell=True)

        def copy2clip_windows(txt):
            cmd = 'echo ' + txt.strip() + '|clip'
            return subprocess.check_call(cmd, shell=True)

        def copy2clip_data_item_paths(*args):
            data_items = document_controller._document_controller.selected_data_items

            paths = []
            for data_item in data_items:
                if data_item is not None:
                    path = data_item.persistent_storage.get_storage_property(data_item, 'file_path')
                    paths.append(f"'{path}'")
                else:
                    paths.append(None)

            try:
                copy2clip_unix(str(paths))
            except subprocess.CalledProcessError:
                copy2clip_windows(str(paths))

        widget.on_clicked = copy2clip_data_item_paths

        main_column.add(widget)
        return main_column


class PathExporterExtension:
    extension_id = "nion.swift.extension.path_exporter"

    def __init__(self, api_broker):
        api = api_broker.get_api(version='~1.0', ui_version='~1.0')
        self.__panel_ref = api.create_panel(PathExporterPanelDelegate(api))

    def close(self):
        self.__panel_ref.close()
        self.__panel_ref = None
