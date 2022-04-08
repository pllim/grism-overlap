import unittest

from grism_overlap import grism_overlap_gui as go


class TestGui(unittest.TestCase):

    # this will run on a separate thread.
    async def _start_app(self):
        self.app.mainloop()

    def setUp(self):
        self.app = go.grismOverlap(root)
        self._start_app()

    def tearDown(self):
        self.app.destroy()

    def test_startup(self):
        title = self.app.winfo_toplevel().title()
        expected = 'The Application My Boss Wants Me To Make'
        self.assertEqual(title, expected)