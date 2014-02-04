# -*- coding: utf-8 -*-

from Products.Five import BrowserView
from Products.GenericSetup.context import TarballExportContext
from Products.GenericSetup.context import TarballImportContext
from Products.GenericSetup.interfaces import IFilesystemExporter
from Products.GenericSetup.interfaces import IFilesystemImporter
from Products.statusmessages.interfaces import IStatusMessage
from collective.formulator import formulatorMessageFactory as _
from collective.formulator.interfaces import IFormulatorImportFormSchema
from plone.z3cform import layout
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zope.component import getMultiAdapter
try:
    # flake8: noqa
    from plone.dexterity.exportimport import DexterityContentExporterImporter
    has_export = True
except ImportError:
    has_export = False


class FormulatorExportView(BrowserView):

    """See ..interfaces.exportimport.IFormulatorExportView
    """

    def __call__(self):
        """See ..interfaces.exportimport.IFormulatorExportView.__call__
        """
        if not has_export:
            return
        ctx = TarballExportContext(self.context)

        self.request.RESPONSE.setHeader('Content-type', 'application/x-gzip')
        self.request.RESPONSE.setHeader('Content-disposition',
                                        'attachment; filename="{0}"'.format(ctx.getArchiveFilename()))

        # export the structure treating the current form as our root context
        IFilesystemExporter(self.context).export(ctx, 'structure', True)

        return ctx.getArchive()


class FormulatorImportForm(form.Form):

    """The form class for importing of exported formulators
    """
    fields = field.Fields(IFormulatorImportFormSchema)
    ignoreContext = True
    ignoreReadonly = True

    @button.buttonAndHandler(_(u'import'), name='import')
    def handleImport(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        if not has_export:
            return

        ctx = TarballImportContext(self.context, data['upload'])
        IFilesystemImporter(self.context).import_(ctx, 'structure', True)

        self.status = _(u'Form imported.')
        message = _(u'Form imported.')
        IStatusMessage(self.request).addStatusMessage(message, type='info')

        url = getMultiAdapter(
            (self.context, self.request), name='absolute_url')()
        self.request.response.redirect(url)


FormulatorImportView = layout.wrap_form(FormulatorImportForm)
