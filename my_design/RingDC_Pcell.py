from si_fab import all as pdk
# from ipkiss3 import all as i3
from ipkiss3 import all as i3
from cell_DC9010 import Direction_coupler_90_10
from GACDC_Pcell import GACDC_HT_1
from WaveguideSource_Pcell import WaveguideSource
from picazzo3.wg.spirals import FixedLengthSpiralRounded
from cell_waveguide import customWavegudie

class TempPort(i3.PCell):
    class Layout(i3.LayoutView):
        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name="in", position=(0.0, 0.0), angle=0.0)
            ports += i3.OpticalPort(name="out", position=(0.0, 0.0), angle=180.0)
            return ports

class TempPort_1(i3.PCell):
    class Layout(i3.LayoutView):
        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name="in", position=(0.0, 0.0), angle=180.0)
            ports += i3.OpticalPort(name="out", position=(0.0, 0.0), angle=0.0)
            return ports

RA = i3.SplineRoundingAlgorithm(adiabatic_angles=(45, 45))
wg_t = pdk.SiWireWaveguideTemplate()  # Predefined trace template from si_fab
wg_t.Layout(core_width=0.45)


# spiral = FixedLengthSpiralRounded(total_length=11000.0,
#                            n_o_loops=3,
#                            trace_template=wg_t)
# spiral_lo = spiral.Layout(incoupling_length=10.0,
#                           bend_radius=50.0,
#                           spacing=10,
#                           stub_direction="H",  # either H or V
#                           growth_direction="H",
#                           )
# WaveguideSource = spiral_lo


# class RingDC(i3.PCell):
#     EBL_scan_filed_length = i3.PositiveNumberProperty(default=1000, doc="EBL_scan_filed_length")
#
#     class Layout(i3.LayoutView):
#         def _generate_instances(self, insts):
#             EBL_scan_filed_length = self.EBL_scan_filed_length
#             insts_insts = {
#                 'temp_port_left': TempPort(),
#                 'temp_port_right': TempPort(),
#                 'DC': Direction_coupler_90_10(),
#                 'Ring': pdk.Ring_FSR400G(),
#             }
#             insts_specs = [
#                 i3.Place('temp_port_left:in', (0, 0)),
#                 i3.Place('temp_port_right:in', (EBL_scan_filed_length, 0)),
#                 i3.PlaceRelative('DC:in', 'temp_port_left:in', (EBL_scan_filed_length / 2, 0)),
#                 i3.PlaceRelative('Ring:in', 'DC:out90', (EBL_scan_filed_length / 10, 0)),
#                 i3.ConnectManhattan([
#                     ('temp_port_left:out', 'DC:in'),
#                     ('Ring:in', 'DC:out90'),
#                     ('Ring:out', 'temp_port_right:in'),
#                 ])
#             ]
#             insts += i3.place_and_route(
#                 insts=insts_insts,
#                 specs=insts_specs
#             )
#             return insts
#
#         def _generate_ports(self, ports):
#             ports += i3.expose_ports(self.instances,
#                                      {
#                                          'temp_port_left:in': 'in',
#                                          'temp_port_right:out': 'out',
#                                          'DC:out10': 'DC_out10',
#                                      })
#             return ports


# class RingDCWaveguide(i3.PCell):
#     EBL_scan_filed_length = i3.PositiveNumberProperty(default=1000, doc="EBL_scan_filed_length")
#
#     class Layout(i3.LayoutView):
#         def _generate_instances(self, insts):
#             EBL_scan_filed_length = self.EBL_scan_filed_length
#             insts_insts = {
#                 'temp_port_left': TempPort(),
#                 'temp_port_right': TempPort(),
#                 'DC': Direction_coupler_90_10(),
#                 'Ring': pdk.Ring_FSR400G(),
#                 'Waveguide': spiral_lo,
#             }
#             insts_specs = [
#                 i3.Place('temp_port_left:in', (0, 0)),
#                 i3.Place('temp_port_right:in', (EBL_scan_filed_length, 0)),
#                 i3.PlaceRelative('DC:in', 'temp_port_left:in', (EBL_scan_filed_length / 10, 0)),
#                 i3.PlaceRelative('Ring:in', 'DC:out90', (EBL_scan_filed_length / 10, 0)),
#                 i3.PlaceRelative('Waveguide:in', 'Ring:out', (EBL_scan_filed_length / 10, 0)),
#                 i3.ConnectManhattan([
#                     ('temp_port_left:out', 'DC:in'),
#                     ('Ring:in', 'DC:out90'),
#                     ('Waveguide:in', 'Ring:out'),
#                     ('Waveguide:out', 'temp_port_right:in'),
#                 ])
#             ]
#             insts += i3.place_and_route(
#                 insts=insts_insts,
#                 specs=insts_specs
#             )
#             return insts
#
#         def _generate_ports(self, ports):
#             ports += i3.expose_ports(self.instances,
#                                      {
#                                          'temp_port_left:in': 'in',
#                                          'temp_port_right:out': 'out',
#                                          'DC:out10': 'DC_out10',
#                                      })
#             return ports


class BPFDcWaveguide(i3.PCell):
    EBL_scan_filed_length = i3.PositiveNumberProperty(default=1000, doc="EBL_scan_filed_length")
    lambda_pump = i3.PositiveNumberProperty(default=1.55, doc="desired resonance lambda")
    heater_open = i3.BoolProperty(default='True', doc='False for no heater')
    total_length = i3.PositiveNumberProperty(default=11000, doc="length of the spiral")
    n_o_loops = i3.PositiveNumberProperty(default=3, doc="number of loops of the spiral")
    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            total_length = self.total_length
            n_o_loops = int(self.n_o_loops)
            if total_length > 11000:
                n_o_loops = 4
            if total_length > 15000:
                n_o_loops = 5
            spiral = FixedLengthSpiralRounded(total_length=total_length,
                                              n_o_loops=n_o_loops,
                                              trace_template=wg_t)
            spiral_lo = spiral.Layout(incoupling_length=10.0,
                                      bend_radius=50.0,
                                      spacing=30,
                                      stub_direction="H",  # either H or V
                                      growth_direction="H",
                                      )
            EBL_scan_filed_length = self.EBL_scan_filed_length
            lambda_pump = self.lambda_pump
            insts_insts = {
                'filter': GACDC_HT_1(lambda_resonance=lambda_pump),
                'temp_port_left': TempPort_1(),
                'temp_port_right': TempPort_1(),
                'temp_port_add': TempPort(),
                'temp_port_through': TempPort(),
                # 'DC': Direction_coupler_90_10(),
                'Waveguide': spiral_lo,
            }
            insts_specs = [
                i3.Place('temp_port_left:in', (0, 0)),
                i3.FlipV('filter'),

                i3.PlaceRelative('filter:in', 'temp_port_left:in', (EBL_scan_filed_length / 20, 0)),
                # i3.PlaceRelative('DC:in', 'filter:drop', (EBL_scan_filed_length / 40, EBL_scan_filed_length / 20)),
                # i3.PlaceRelative('Waveguide:in', 'DC:out90', (EBL_scan_filed_length / 40 + 10, 0)),
                i3.PlaceRelative('Waveguide:in', 'filter:drop', (EBL_scan_filed_length / 40 + 10, EBL_scan_filed_length / 20)),
                i3.PlaceRelative('temp_port_add:in', 'temp_port_left:in', (0, -400)),
                i3.PlaceRelative('temp_port_through:in', 'temp_port_left:in', (0, -200)),
                i3.PlaceRelative('temp_port_right:in', 'Waveguide:out', (120, 0)),
                i3.ConnectManhattan([
                    ('filter:in', 'temp_port_left:out'),
                    ('filter:drop', 'Waveguide:in'),
                    # ('filter:add', 'temp_port_add:in'),
                    ('filter:through', 'temp_port_through:in'),
                    # ('Waveguide:in', 'DC:out90'),
                    ('Waveguide:out', 'temp_port_right:in'),
                ],
                bend_radius=20),
                i3.ConnectManhattan([
                    ('filter:add', 'temp_port_add:in'),
                ],
                    bend_radius=20,
                    control_points=[i3.START + (50, 0)]
                )
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
                                         'temp_port_through:out': 'through',
                                         'temp_port_add:out': 'add',
                                         # 'DC:out10': 'DC_out10',
                                     })
            if self.heater_open:
                ports += i3.expose_ports(self.instances,
                                         {
                                             'filter:elec1': 'elec1',
                                             'filter:elec2': 'elec2',
                                         })
            return ports


class BPFDcRing(i3.PCell):
    EBL_scan_filed_length = i3.PositiveNumberProperty(default=1000, doc="EBL_scan_filed_length")
    lambda_pump = i3.PositiveNumberProperty(default=1.55, doc="desired resonance lambda")
    heater_open = i3.BoolProperty(default='True', doc='False for no heater')
    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            EBL_scan_filed_length = self.EBL_scan_filed_length
            lambda_pump = self.lambda_pump
            insts_insts = {
                'filter': GACDC_HT(lambda_resonance=lambda_pump),
                'temp_port_left': TempPort(),
                'temp_port_right': TempPort(),
                'Ring': pdk.Ring_FSR200G(),
                'DC': Direction_coupler_90_10(),
                'DC_2': Direction_coupler_90_10(),
                # 'Waveguide': spiral_lo,
            }
            insts_specs = [
                i3.Place('temp_port_left:in', (0, 0)),
                i3.FlipV('filter'),
                i3.Place('temp_port_right:in', (EBL_scan_filed_length, 50.825)),
                i3.PlaceRelative('filter:in', 'temp_port_left:in', (EBL_scan_filed_length / 20, 0)),
                i3.PlaceRelative('DC:in', 'filter:drop', (EBL_scan_filed_length / 40, EBL_scan_filed_length / 20)),
                i3.PlaceRelative('Ring:in', 'DC:out90', (EBL_scan_filed_length / 10, 0)),
                i3.PlaceRelative('DC_2:in', 'Ring:out', (EBL_scan_filed_length / 10, 0)),
                i3.ConnectManhattan([
                    ('filter:in', 'temp_port_left:out'),
                    ('filter:drop', 'DC:in'),
                    ('Ring:in', 'DC:out90'),
                    ('Ring:out', 'DC_2:in'),
                    ('DC_2:out90', 'temp_port_right:in'),
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
                                         'filter:through': 'through',
                                         'DC:out10': 'DC_out10',
                                         'DC_2:out10': 'DC_2_out10',
                                     })
            if self.heater_open:
                ports += i3.expose_ports(self.instances,
                                         {
                                             'filter:elec1': 'elec2',
                                             'filter:elec2': 'elec3',
                                             'Ring:elec1': 'elec1',
                                             'Ring:elec2': 'elec4',
                                         })
            return ports


class DcWaveguide(i3.PCell):
    EBL_scan_filed_length = i3.PositiveNumberProperty(default=1000, doc="EBL_scan_filed_length")
    lambda_resonance = i3.PositiveNumberProperty(default=1.55, doc="desired resonance lambda")
    heater_open = i3.BoolProperty(default='True', doc='False for no heater')
    total_length = i3.PositiveNumberProperty(default=11000, doc="length of the spiral")
    n_o_loops = i3.PositiveNumberProperty(default=3, doc="number of loops of the spiral")

    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            EBL_scan_filed_length = self.EBL_scan_filed_length
            total_length = self.total_length
            n_o_loops = int(self.n_o_loops)
            if total_length > 11000:
                n_o_loops = 4
            if total_length > 15000:
                n_o_loops = 5
            spiral = FixedLengthSpiralRounded(total_length=total_length,
                                              n_o_loops=n_o_loops,
                                              trace_template=wg_t)
            spiral_lo = spiral.Layout(incoupling_length=10.0,
                                      bend_radius=50.0,
                                      spacing=30,
                                      stub_direction="H",  # either H or V
                                      growth_direction="H",
                                      )
            insts_insts = {
                'temp_port_left': TempPort(),
                'temp_port_right': TempPort(),
                'DC': Direction_coupler_90_10(),
                'Waveguide': spiral_lo,
            }
            insts_specs = [
                i3.Place('temp_port_left:in', (0, 0)),
                i3.Place('temp_port_right:in', (EBL_scan_filed_length, 0)),
                i3.PlaceRelative('DC:in', 'temp_port_left:in', (EBL_scan_filed_length / 20, 0)),
                i3.PlaceRelative('Waveguide:in', 'DC:out90', (EBL_scan_filed_length / 40 + 10, 0)),
                i3.ConnectManhattan([
                    ('DC:in', 'temp_port_left:out'),
                    ('Waveguide:in', 'DC:out90'),
                    ('Waveguide:out', 'temp_port_right:in'),
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
                                         'DC:out10': 'DC_out10',
                                     })
            if self.heater_open:
                ports += i3.expose_ports(self.instances,
                                         {

                                         })
            return ports


# class RingDC(i3.PCell):
#     EBL_scan_filed_length = i3.PositiveNumberProperty(default=1000, doc="EBL_scan_filed_length")
#     lambda_pump = i3.PositiveNumberProperty(default=1.55, doc="desired resonance lambda")
#     heater_open = i3.BoolProperty(default='True', doc='False for no heater')
#     class Layout(i3.LayoutView):
#         def _generate_instances(self, insts):
#             EBL_scan_filed_length = self.EBL_scan_filed_length
#             lambda_pump = self.lambda_pump
#             insts_insts = {
#                 # 'filter': GACDC_HT(lambda_resonance=lambda_pump),
#                 'temp_port_left': TempPort_1(),
#                 'temp_port_right': TempPort_1(),
#                 'Ring': pdk.Ring_FSR200G(),
#                 'DC': Direction_coupler_90_10(),
#                 # 'DC_2': Direction_coupler_90_10(),
#                 # 'Waveguide': spiral_lo,
#             }
#             insts_specs = [
#                 i3.Place('temp_port_left:in', (0, 0)),
#                 # i3.FlipV('filter'),
#                 i3.Place('temp_port_right:in', (EBL_scan_filed_length, 0)),
#                 # i3.PlaceRelative('filter:in', 'temp_port_left:in', (EBL_scan_filed_length / 20, 0)),
#                 i3.PlaceRelative('DC:in', 'temp_port_left:out', (10, 0)),
#                 i3.PlaceRelative('Ring:in', 'DC:out90', (EBL_scan_filed_length / 10, 0)),
#                 i3.ConnectManhattan([
#                     ('DC:in', 'temp_port_left:out'),
#                     # ('filter:drop', 'DC:in'),
#                     ('Ring:in', 'DC:out90'),
#                     ('Ring:out', 'temp_port_right:in'),
#                     # ('DC_2:out90', 'temp_port_right:in'),
#                 ])
#             ]
#             insts += i3.place_and_route(
#                 insts=insts_insts,
#                 specs=insts_specs
#             )
#             return insts
#
#         def _generate_ports(self, ports):
#             ports += i3.expose_ports(self.instances,
#                                      {
#                                          'temp_port_left:in': 'in',
#                                          'temp_port_right:out': 'out',
#                                          # 'filter:through': 'through',
#                                          'DC:out10': 'DC_out10',
#                                          # 'DC_2:out10': 'DC_2_out10',
#                                      })
#             if self.heater_open:
#                 ports += i3.expose_ports(self.instances,
#                                          {
#                                              # 'filter:elec1': 'elec2',
#                                              # 'filter:elec2': 'elec3',
#                                              'Ring:elec1': 'elec1',
#                                              'Ring:elec2': 'elec2',
#                                          })
#             return ports


class BPFDcCustomWaveguide(i3.PCell):
    EBL_scan_filed_length = i3.PositiveNumberProperty(default=1000, doc="EBL_scan_filed_length")
    lambda_resonance = i3.PositiveNumberProperty(default=1.55, doc="desired resonance lambda")
    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            EBL_scan_filed_length = self.EBL_scan_filed_length
            insts_insts = {
                'filter': GACDC_HT(lambda_resonance=1.55),
                'temp_port_left': TempPort(),
                'temp_port_right': TempPort(),
                'DC': Direction_coupler_90_10(),
                'Waveguide': customWavegudie(),
            }
            insts_specs = [
                i3.Place('temp_port_left:in', (0, 0)),
                i3.FlipV('filter'),
                i3.Place('temp_port_right:in', (EBL_scan_filed_length, 50.825)),
                i3.PlaceRelative('filter:in', 'temp_port_left:in', (EBL_scan_filed_length / 20, 0)),
                i3.PlaceRelative('DC:in', 'filter:drop', (EBL_scan_filed_length / 20, EBL_scan_filed_length / 20)),
                i3.PlaceRelative('Waveguide:in', 'DC:out90', (EBL_scan_filed_length / 10, 0)),
                i3.ConnectManhattan([
                    ('filter:in', 'temp_port_left:out'),
                    ('filter:drop', 'DC:in'),
                    ('Waveguide:in', 'DC:out90'),
                    ('Waveguide:out', 'temp_port_right:in'),
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
                                         'filter:through': 'through',
                                         'DC:out10': 'DC_out10',
                                     })
            return ports


if __name__ == '__main__':
    # pass
    # lo1 = RingDC()
    # lo = RingDCWaveguide()
    lo = BPFDcWaveguide(total_length=12000)
    # lo = DcWaveguide(total_length=19000)
    # lo = pdk.Ring_FSR200G()
    # lo = BPFDcRing()
    # lo = BPFDcCustomWaveguide()
    # lo = GACDCPhaseShiftApodized(grating_period=0.3271)
    # lo = GACDC_HT(grating_period=0.3271)
    # spiral_lo.write_gdsii('Spiral.gds')
    # lo.Layout().visualize(annotate=True)
    # lo1.Layout().write_gdsii('RingDC.gds')
    lo.Layout().write_gdsii('BPFDcWaveguide.gds')
