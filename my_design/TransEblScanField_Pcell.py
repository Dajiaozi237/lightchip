from si_fab import all as pdk
# from ipkiss3 import all as i3
from ipkiss3 import all as i3


class TempPort(i3.PCell):
    class Layout(i3.LayoutView):
        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name="in", position=(0.0, 0.0), angle=180.0)
            ports += i3.OpticalPort(name="out", position=(0.0, 0.0), angle=0.0)
            return ports


class TransEblScanField(i3.PCell):
    EBL_scan_filed_length = i3.PositiveNumberProperty(default=1000, doc="EBL_scan_filed_length")

    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            EBL_scan_filed_length = self.EBL_scan_filed_length
            insts_insts = {
                'temp_port_left': TempPort(),
                'temp_port_right': TempPort(),
            }
            insts_specs = [
                i3.Place('temp_port_left:in', (0, 0)),
                i3.Place('temp_port_right:in', (EBL_scan_filed_length, 0)),
                i3.ConnectManhattan([
                    ('temp_port_left:out', 'temp_port_right:in'),
                ])
            ]
            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            ports += i3.expose_ports(self.instances,
                                     {
                                         'temp_port_left:in': 'in',
                                         'temp_port_right:out': 'out',
                                     })
            return ports


if __name__ == '__main__':
    # pass
    lo = TransEblScanField()
    # lo = GACDCPhaseShiftApodized(grating_period=0.3271)
    # lo = GACDC_HT(grating_period=0.3271)

    lo.Layout().visualize(annotate=True)
    lo.Layout().write_gdsii('Trans.gds')
