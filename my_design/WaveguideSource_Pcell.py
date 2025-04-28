# Importing silicon_photonics technology and IPKISS

# import technologies.silicon_photonics
# from si_fab import all as pdk
from si_fab import all as pdk
# from ipkiss3 import all as i3
from ipkiss3 import all as i3
from picazzo3.wg.spirals import FixedLengthSpiralRounded
from picazzo3.traces.rib_wg.trace import RibWaveguideTemplate
from picazzo3.traces.wire_wg.trace import WireWaveguideTemplate
from euler90_rounding_algorithm import Euler90Algorithm
from si_fab.technology import TECH


RA = i3.SplineRoundingAlgorithm(adiabatic_angles=(45, 45))
wg_t = pdk.SiWireWaveguideTemplate()  # Predefined trace template from si_fab
wg_t.Layout(core_width=0.45)


spiral = FixedLengthSpiralRounded(total_length=12000.0,
                           n_o_loops=5,
                           trace_template=wg_t)
spiral_lo = spiral.Layout(incoupling_length=200.0,
                          bend_radius=50.0,
                          spacing=10,
                          stub_direction="V",  # either H or V
                          growth_direction="V",
                          )
# WaveguideSource = spiral_lo


class TempPort(i3.PCell):
    class Layout(i3.LayoutView):
        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name="in", position=(0.0, 0.0), angle=180.0)
            ports += i3.OpticalPort(name="out", position=(0.0, 0.0), angle=0.0)
            return ports


class WaveguideSource(i3.PCell):
    """
    Spiral Waveguide Source
    """
    _name_prefix = "WaveguideSource"
    EBL_scan_filed_length = i3.PositiveNumberProperty(default=1000, doc="EBL_scan_filed_length")

    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            EBL_scan_filed_length = self.EBL_scan_filed_length
            insts_insts = {
                'spiral': spiral_lo,
                'temp_port': TempPort(),
                # 'temp_port_right': TempPort(),
            }

            insts_specs = [
                i3.Place('spiral:in', (0, 0)),
                i3.Place('temp_port:in', (EBL_scan_filed_length, 0)),
                i3.ConnectManhattan([
                    ('spiral:out', 'temp_port:in'),
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
                                         'spiral:in': 'in',
                                         'temp_port:out': 'out',
                                     })
            return ports


# spiral_lo.visualize(annotate=True)
#
# spiral_lo.write_gdsii("spiral_12000.gds")
#
# print("The length of the spiral is {} um".format(spiral_lo.trace_length()))

# ring = pdk.Ring_FSR400G()
# ring_lo = ring.Layout(radius=55.)
# ring_lo.write_gdsii("ring_test.gds")
if __name__ == '__main__':
    # pass
    lo = WaveguideSource()
    # lo = GACDCPhaseShiftApodized(grating_period=0.3271)
    # lo = GACDC_HT(grating_period=0.3271)

    lo.Layout().visualize(annotate=True)
    lo.Layout().write_gdsii('WaveguideSource.gds')
    # print("The length of the spiral is {} um".format(spiral_lo.trace_length()))