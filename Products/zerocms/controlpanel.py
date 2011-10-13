# -*- coding: utf-8

from plone.app.registry.browser import controlpanel

from Products.zerocms.interfaces import IZeroCMSSettings, IZeroCMSSchema, _


class ZeroCMSSettingsEditForm(controlpanel.RegistryEditForm):
    """from: http://plone.org/documentation/kb/how-to-create-a-plone-control-panel-with-plone.app.registry
       @author: Tarjei Huse (tarjei@scanmine.com)
       """

    schema = IZeroCMSSchema
    label = _(u"ZeroCMS settings")
    description = _(u"""""")

    def updateFields(self):
        super(ZeroCMSSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(ZeroCMSSettingsEditForm, self).updateWidgets()

class ZeroCMSSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = ZeroCMSSettingsEditForm

