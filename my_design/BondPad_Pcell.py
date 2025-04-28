from si_fab import all as pdk
from ipkiss3 import all as i3


Lm1 = i3.TECH.PPLAYER.M1
Layer_window = i3.TECH.PPLAYER.CON


class BondPad(i3.Circuit):
    """
    electric pads
    """
    pad_width_x = i3.PositiveNumberProperty(default=200.0, doc=".")
    pad_width_y = i3.PositiveNumberProperty(default=350.0, doc=".")
    pad_open_width_x = i3.PositiveNumberProperty(default=190.0, doc=".")
    pad_open_width_y = i3.PositiveNumberProperty(default=340.0, doc=".")
    wirewidth = i3.PositiveNumberProperty(default=10.0, doc="width of the electric wire")
    class Layout(i3.LayoutView):

        def _generate_elements(self, elems):
            pad_width_x = self.pad_width_x
            pad_width_y = self.pad_width_y
            pad_open_width_x = self.pad_open_width_x
            pad_open_width_y = self.pad_open_width_y
            elems += i3.Rectangle(
                layer=Lm1,
                center=(0, 0),
                box_size=(pad_width_x, pad_width_y),
            )
            elems += i3.Rectangle(
                layer=Layer_window,
                center=(0, 0),
                box_size=(pad_open_width_x, pad_open_width_y),
            )
            return elems

        def _generate_ports(self, ports):
            pad_width_y = self.pad_width_y
            wirewidth = self.wirewidth
            tt = i3.ElectricalWireTemplate()
            tt.Layout(width=wirewidth, layer=i3.TECH.PPLAYER.M1)
            ports += i3.ElectricalPort(
                name="port",
                position=(0, pad_width_y / 2),
                angle=90.0,
                trace_template=tt,
            )
            return ports


if __name__ == '__main__':
    # pass
    lo = BondPad()
    lo.Layout().visualize(annotate=True)
    lo.Layout().write_gdsii('Direction_coupler_90_10.gds')
