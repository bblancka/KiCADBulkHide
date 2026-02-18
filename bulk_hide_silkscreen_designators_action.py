#!/usr/bin/env python
import pcbnew
import os.path
import wx

class BulkHideSilkscreenDesignators(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Bulk hide silkscreen designators"
        self.category = "Silkscreen"
        self.description = "Hide reference designators or values for selected footprints"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'icon.png')

    def Run(self):
        # Filter just selected footprints
        selected_footprints: list[pcbnew.FOOTPRINT] = [
            footprint for footprint in pcbnew.GetCurrentSelection()
            if type(footprint).__name__ == 'FOOTPRINT'
        ]
        
        if len(selected_footprints) == 0:
            # Show info dialog
            dlg = wx.MessageDialog(
                None, 
                "Please select one or multiple footprints!\n...or use Ctrl+A to select everything.", 
                "No footprints selected", 
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Create dialog to choose what to hide
        choices = ["Reference (e.g., R1, C2, U3)", "Value (e.g., 10k, 100nF)", "Both Reference and Value"]
        dlg = wx.SingleChoiceDialog(
            None,
            "What do you want to hide on the selected footprints?",
            "Choose attribute to hide",
            choices
        )
        
        if dlg.ShowModal() == wx.ID_OK:
            selection = dlg.GetSelection()
            dlg.Destroy()
            
            hide_reference = selection in [0, 2]  # Hide reference if "Reference" or "Both" selected
            hide_value = selection in [1, 2]      # Hide value if "Value" or "Both" selected
            
            for selected_footprint in selected_footprints:
                # Hide reference if selected
                if hide_reference:
                    reference = selected_footprint.Reference()
                    if reference:
                        reference.SetVisible(False)
                
                # Hide value if selected
                if hide_value:
                    value = selected_footprint.Value()
                    if value:
                        value.SetVisible(False)
            
            pcbnew.Refresh()
        else:
            dlg.Destroy()

BulkHideSilkscreenDesignators().register()
