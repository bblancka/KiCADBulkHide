#!/usr/bin/env python
import pcbnew
import os.path
import wx

# Text field types that may be selected instead of footprints
TEXT_FIELD_TYPES = ['PCB_TEXT', 'FP_TEXT', 'PCB_FIELD']

class BulkHideSilkscreenDesignators(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Bulk hide silkscreen designators"
        self.category = "Silkscreen"
        self.description = "Hide reference designators or values for selected footprints"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'icon.png')

    def Run(self):
        selection = pcbnew.GetCurrentSelection()

        # Build set of footprints from selection
        # Handle both direct footprint selection and text field selection
        footprint_set = set()

        for item in selection:
            item_type = type(item).__name__

            if item_type == 'FOOTPRINT':
                # Direct footprint selection
                footprint_set.add(item)
            elif item_type in TEXT_FIELD_TYPES:
                # Text field selected - find parent footprint
                parent = item.GetParent()
                if parent and type(parent).__name__ == 'FOOTPRINT':
                    footprint_set.add(parent)

        # Convert set to list
        selected_footprints = list(footprint_set)
        
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

        # Create custom dialog with checkboxes
        dlg = wx.Dialog(None, title="Choose what to hide", style=wx.DEFAULT_DIALOG_STYLE)
        
        # Create panel and sizer
        panel = wx.Panel(dlg)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Add instruction text
        instruction = wx.StaticText(panel, label="Select what to hide on the selected footprints:")
        sizer.Add(instruction, 0, wx.ALL, 10)
        
        # Add checkboxes (both checked by default)
        cb_reference = wx.CheckBox(panel, label="Hide Reference (e.g., R1, C2, U3)")
        cb_reference.SetValue(True)
        sizer.Add(cb_reference, 0, wx.ALL, 5)
        
        cb_value = wx.CheckBox(panel, label="Hide Value (e.g., 10k, 100nF)")
        cb_value.SetValue(True)
        sizer.Add(cb_value, 0, wx.ALL, 5)
        
        # Add OK/Cancel buttons
        btn_sizer = wx.StdDialogButtonSizer()
        btn_ok = wx.Button(panel, wx.ID_OK)
        btn_cancel = wx.Button(panel, wx.ID_CANCEL)
        btn_sizer.AddButton(btn_ok)
        btn_sizer.AddButton(btn_cancel)
        btn_sizer.Realize()
        sizer.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 10)
        
        panel.SetSizer(sizer)
        sizer.Fit(dlg)
        
        if dlg.ShowModal() == wx.ID_OK:
            hide_reference = cb_reference.GetValue()
            hide_value = cb_value.GetValue()
            
            # Validate that at least one option is selected
            if not hide_reference and not hide_value:
                dlg.Destroy()
                warning_dlg = wx.MessageDialog(
                    None,
                    "Please select at least one option to hide.",
                    "No option selected",
                    wx.OK | wx.ICON_WARNING
                )
                warning_dlg.ShowModal()
                warning_dlg.Destroy()
                return
            
            dlg.Destroy()
            
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
