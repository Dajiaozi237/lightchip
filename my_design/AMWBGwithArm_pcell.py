from si_fab import all as pdk
from ipkiss3 import all as i3
from si_fab.technology import TECH
from picazzo3.wg.bend import WgBend90
from GACDC_Pcell import GACDC_HT
from ECrow_Pcell import ECrow


class TextPCell(i3.PCell):
    # _name_prefix = "Text"
    text = i3.StringProperty(doc='display', default=' ')

    class Layout(i3.LayoutView):
        # n_rows = i3.IntProperty(doc="Number of GC rows", default=0)
        def _generate_elements(self, elems):
            labelText = self.text
            elems = i3.PolygonText(
                layer=TECH.PPLAYER.DOC,
                # layer=TECH.PPLAYER.NONE,
                text=labelText,
                alignment=(i3.TEXT.ALIGN.LEFT, i3.TEXT.ALIGN.TOP),
                coordinate=(0, 0.),
                font=0, height=30
            )
            return elems

        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name='LOC', position=(0, 0.), angle=0)
            return ports


class TempPort(i3.PCell):
    """
       in       ---------------------------------    out
    """
    class Layout(i3.LayoutView):
        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name="in", position=(0.0, 0.0), angle=180.0)
            ports += i3.OpticalPort(name="out", position=(0.0, 0.0), angle=0.0)
            return ports


class custom_elec_single(i3.PCell):
    _name_prefix = "custom_elec"
    heater_width = i3.PositiveNumberProperty(default=3.6, doc="Width of the heater")
    heater_length = i3.PositiveNumberProperty(default=900., doc="heater_length")
    m1_taper_width = i3.PositiveNumberProperty(default=50., doc="Width of the M1 contact")
    m1_taper_length = i3.PositiveNumberProperty(default=50., doc="Length of the M1 contacst")
    m1_taper_wider = i3.PositiveNumberProperty(default=2., doc="M1 width of the end of M1 taper")
    overlap_heater_m1 = i3.PositiveNumberProperty(default=5., doc="overlap_heater_m1")

    class Layout(i3.LayoutView):
        def _generate_elements(self, elems):
            heater_length = self.heater_length
            heater_width = self.heater_width
            m1_taper_width = self.m1_taper_width
            m1_taper_length = self.m1_taper_length
            overlap_heater_m1 = self.overlap_heater_m1
            m1_taper_wider = self.m1_taper_wider
            Lh = i3.TECH.PPLAYER.HT
            Lm1 = i3.TECH.PPLAYER.M1

            elems += i3.Rectangle(layer=Lh,
                                  center=(0, 0),
                                  # box_size=(Width2, Length))
                                  box_size=(heater_length, heater_width))
            elems += i3.Wedge(
                layer=Lm1,
                begin_coord=(-heater_length / 2 + overlap_heater_m1, 0),
                end_coord=(-heater_length / 2 - m1_taper_length, 0.),
                begin_width=heater_width + m1_taper_wider * 2,
                end_width=m1_taper_width,
            )
            elems += i3.Wedge(
                layer=Lm1,
                begin_coord=(heater_length / 2 - overlap_heater_m1, 0),
                end_coord=(heater_length / 2 + m1_taper_length, 0.),
                begin_width=heater_width + m1_taper_wider * 2,
                end_width=m1_taper_width,
            )
            return elems

        def _generate_ports(self, ports):
            wirewidth = 10
            heater_length = self.heater_length
            heater_width = self.heater_width
            m1_taper_width = self.m1_taper_width
            m1_taper_length = self.m1_taper_length
            overlap_heater_m1 = self.overlap_heater_m1
            tt = i3.ElectricalWireTemplate()
            tt.Layout(width=wirewidth, layer=i3.TECH.PPLAYER.M1)
            Lh = i3.TECH.PPLAYER.HT
            Lm1 = i3.TECH.PPLAYER.M1
            ports += i3.ElectricalPort(name='elec1',
                                       position=(heater_length / 2 + m1_taper_length, 0),
                                       layer=i3.TECH.PPLAYER.M1,
                                       angle=0,
                                       trace_template=tt,
                                       )
            ports += i3.ElectricalPort(name='elec2',
                                       position=(-heater_length / 2 - m1_taper_length, 0),
                                       layer=i3.TECH.PPLAYER.M1,
                                       angle=180,
                                       trace_template=tt,
                                       )
            ports += i3.OpticalPort(name='left_loc_of_heater', position=(-heater_length / 2, 0), )
            return ports


bend90_a = WgBend90(trace_template=pdk.SiWireWaveguideTemplate())
bend90_a = bend90_a.Layout(quadrant=1, bend_radius=10.0)
bend90_d = WgBend90(trace_template=pdk.SiWireWaveguideTemplate())
bend90_d = bend90_d.Layout(quadrant=-2, bend_radius=10.0)
bend_in_out1 = i3.Circuit(
    insts={
        'bend90_ua': bend90_a,
        'bend90_ud': bend90_d,
    },
    specs=[
        # i3.ConnectManhattan('bend90_ua:in', 'bend90_ud:out'),
        i3.FlipV("bend90_ua"),
        i3.FlipV("bend90_ud"),
        i3.PlaceRelative('bend90_ua:in', 'bend90_ud:out', (0, -50.)),
        i3.ConnectManhattan('bend90_ua:in', 'bend90_ud:out'),
    ],
    exposed_ports={'bend90_ua:out': 'in', 'bend90_ud:in': 'out'},
    name=f'bendInWBG1',
)
bend_in_out2 = i3.Circuit(
    insts={
        'bend90_ua': bend90_a,
        'bend90_ud': bend90_d,
    },
    specs=[
        i3.FlipV("bend90_ua"),
        i3.FlipV("bend90_ud"),
        # i3.ConnectManhattan('bend90_ua:in', 'bend90_ud:out'),
        i3.PlaceRelative('bend90_ua:in', 'bend90_ud:out', (0, -50.)),
        i3.ConnectManhattan('bend90_ua:in', 'bend90_ud:out'),
    ],
    exposed_ports={'bend90_ua:out': 'in', 'bend90_ud:in': 'out'},
    name=f'bendInWBG2',
)
bend_in_out3 = i3.Circuit(
    insts={
        'bend90_ua': bend90_a,
        'bend90_ud': bend90_d,
    },
    specs=[
        # i3.ConnectManhattan('bend90_ua:in', 'bend90_ud:out'),
        i3.PlaceRelative('bend90_ua:in', 'bend90_ud:out', (0, 50.)),
        i3.ConnectManhattan('bend90_ua:in', 'bend90_ud:out'),
    ],
    exposed_ports={'bend90_ua:out': 'in', 'bend90_ud:in': 'out'},
    name=f'bendInWBG3',
)
bend_in_out4 = i3.Circuit(
    insts={
        'bend90_ua': bend90_a,
        'bend90_ud': bend90_d,
    },
    specs=[
        # i3.ConnectManhattan('bend90_ua:in', 'bend90_ud:out'),
        i3.PlaceRelative('bend90_ua:in', 'bend90_ud:out', (0, 50.)),
        i3.ConnectManhattan('bend90_ua:in', 'bend90_ud:out'),
    ],
    exposed_ports={'bend90_ua:out': 'in', 'bend90_ud:in': 'out'},
    name=f'bendInWBG4',
)
class AMWBGwithArm(i3.PCell):
    _name_prefix = "AMWBGwithArm"
    wbg_length = i3.PositiveNumberProperty(doc=" ", default=900.0)
    period = i3.PositiveNumberProperty(doc=" ", default=0.2965)
    grating_width = i3.NonNegativeNumberProperty(doc=" ", default=0.163)
    apodization = i3.NonNegativeNumberProperty(doc="", default=200.0)
    apFunction = i3.StringProperty(default="Blackman", doc="type of waveguide: wide or narrow")
    apodization_type = i3.StringProperty(default='DoubleSide', doc="type of waveguide: wide or narrow")
    apodization_loc = i3.StringProperty(default='StartAndEnd', doc="type of waveguide: wide or narrow")
    textMarker = i3.BoolProperty(default=False, doc=".")
    heater_open = i3.BoolProperty(default='True', doc='False for no heater')

    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            wbg_length = self.wbg_length
            period = self.period
            grating_width = self.grating_width
            apodization = self.apodization
            apFunction = self.apFunction
            apodization_type = self.apodization_type
            apodization_loc = self.apodization_loc
            filterWBG = pdk.AMWBG(
                wbg_length=wbg_length,
                wbg_period=period,
                wbg_duty_cycle=0.5,
                wbg_grating_width=grating_width,
                wbg_grating_height=0.15,
                wbg_apodization_length=apodization,
                wbg_waveguide_width=1.,
                taper_length=25.,
                apodization_type=apodization_type,
                apodization_function=apFunction,
                apodization_loc=apodization_loc,
                to_draw_deltaL=False,
            )
            insts_insts = {
                'wbg': filterWBG,
                'inarm': bend_in_out1,
                'outarm': bend_in_out2,
                # 'heater': custom_elec_single(m1_taper_width=30, heater_length=wbg_length),
            }
            insts_specs = [
                # i3.ConnectManhattan('bend90_ua:in', 'bend90_ud:out'),
                i3.Place('wbg:in', (0, 0)),
                # i3.PlaceRelative('heater:left_loc_of_heater', 'wbg:in', (35, 0)),
                i3.PlaceRelative('inarm:out', 'wbg:in', (0, 0)),
                i3.PlaceRelative('outarm:in', 'wbg:out', (0, 0)),
            ]
            if self.heater_open:
                insts_insts['heater'] = custom_elec_single(m1_taper_width=10, heater_length=wbg_length)
                insts_specs.append(i3.PlaceRelative('heater:left_loc_of_heater', 'wbg:in', (35, 0)))
            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            ports += i3.expose_ports(self.instances,
                                     {
                                         'inarm:in': 'in',
                                         'outarm:out': 'out',
                                     })
            if self.heater_open:
                ports += i3.expose_ports(self.instances,
                                         {
                                             'heater:elec1': 'elec2',
                                             'heater:elec2': 'elec1',
                                         })
            return ports


class AMWBGwithArm_sameside(i3.PCell):
    _name_prefix = "AMWBGwithArm_sameside"
    wbg_length = i3.PositiveNumberProperty(doc=" ", default=900.0)
    period = i3.PositiveNumberProperty(doc=" ", default=0.2965)
    grating_width = i3.NonNegativeNumberProperty(doc=" ", default=0.163)
    grating_height = i3.NonNegativeNumberProperty(doc=" ", default=0.15)
    apodization = i3.NonNegativeNumberProperty(doc="", default=300.0)
    apFunction = i3.StringProperty(default="Blackman", doc="type of waveguide: wide or narrow")
    apodization_type = i3.StringProperty(default='DoubleSide', doc="type of waveguide: wide or narrow")
    apodization_loc = i3.StringProperty(default='StartAndEnd', doc="type of waveguide: wide or narrow")
    heater_open = i3.BoolProperty(default=True, doc='False for no heater')
    textMarker = i3.BoolProperty(default=False, doc=".")
    wbg_waveguide_width = i3.PositiveNumberProperty(doc=" ", default=1.)

    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            wbg_length = self.wbg_length
            period = self.period
            grating_width = self.grating_width
            apodization = self.apodization
            apFunction = self.apFunction
            apodization_type = self.apodization_type
            apodization_loc = self.apodization_loc
            wbg_waveguide_width=self.wbg_waveguide_width
            filterWBG = pdk.AMWBG(
                wbg_length=wbg_length,
                wbg_period=period,
                wbg_duty_cycle=0.5,
                wbg_grating_width=grating_width,
                wbg_grating_height=self.grating_height,
                wbg_apodization_length=apodization,
                wbg_waveguide_width=wbg_waveguide_width,
                taper_length=25.,
                apodization_type=apodization_type,
                apodization_function=apFunction,
                apodization_loc=apodization_loc,
                to_draw_deltaL=False,
                textMarker=self.textMarker,
            )
            insts_insts = {
                'wbg': filterWBG,
                'inarm': bend_in_out1,
                'outarm': bend_in_out2,
                # 'heater': custom_elec_single(m1_taper_width=30, heater_length=wbg_length),
                # 'heater': custom_elec_single(m1_taper_width=10, heater_length=wbg_length),
            }

            insts_specs = [
                # i3.ConnectManhattan('bend90_ua:in', 'bend90_ud:out'),
                i3.Place('wbg:in', (0, 0)),
                # i3.PlaceRelative('heater:left_loc_of_heater', 'wbg:in', (35, 0)),
                i3.PlaceRelative('inarm:out', 'wbg:in', (0, 0)),
                i3.PlaceRelative('outarm:in', 'wbg:out', (0, 0)),
                i3.FlipV('outarm'),
            ]
            if self.heater_open:
                insts_insts['heater'] = custom_elec_single(m1_taper_width=10, heater_length=wbg_length)
                insts_specs.append(i3.PlaceRelative('heater:left_loc_of_heater', 'wbg:in', (35, 0)))

            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            ports += i3.expose_ports(self.instances,
                                     {
                                         'inarm:in': 'in',
                                         'outarm:out': 'out',
                                         # 'heater:elec1': 'elec2',
                                         # 'heater:elec2': 'elec1',
                                     })
            if self.heater_open:
                ports += i3.expose_ports(self.instances,
                                         {
                                             'heater:elec1': 'elec2',
                                             'heater:elec2': 'elec1',
                                         })
            return ports

class AMWBGwithArm_sameside_reverse(i3.PCell):
    _name_prefix = "AMWBGwithArm_sameside"
    wbg_length = i3.PositiveNumberProperty(doc=" ", default=900.0)
    period = i3.PositiveNumberProperty(doc=" ", default=0.2965)
    grating_width = i3.NonNegativeNumberProperty(doc=" ", default=0.163)
    grating_height = i3.NonNegativeNumberProperty(doc=" ", default=0.15)
    apodization = i3.NonNegativeNumberProperty(doc="", default=300.0)
    apFunction = i3.StringProperty(default="Blackman", doc="type of waveguide: wide or narrow")
    apodization_type = i3.StringProperty(default='DoubleSide', doc="type of waveguide: wide or narrow")
    apodization_loc = i3.StringProperty(default='StartAndEnd', doc="type of waveguide: wide or narrow")
    heater_open = i3.BoolProperty(default=True, doc='False for no heater')
    textMarker = i3.BoolProperty(default=False, doc=".")
    wbg_waveguide_width=i3.PositiveNumberProperty(doc=" ", default=1.)

    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            wbg_length = self.wbg_length
            period = self.period
            grating_width = self.grating_width
            apodization = self.apodization
            apFunction = self.apFunction
            apodization_type = self.apodization_type
            apodization_loc = self.apodization_loc
            wbg_waveguide_width=self.wbg_waveguide_width
            filterWBG = pdk.AMWBG(
                wbg_length=wbg_length,
                wbg_period=period,
                wbg_duty_cycle=0.5,
                wbg_grating_width=grating_width,
                wbg_grating_height=self.grating_height,
                wbg_apodization_length=apodization,
                wbg_waveguide_width=wbg_waveguide_width,
                taper_length=25.,
                apodization_type=apodization_type,
                apodization_function=apFunction,
                apodization_loc=apodization_loc,
                to_draw_deltaL=False,
                textMarker=self.textMarker,
            )
            insts_insts = {
                'wbg': filterWBG,
                'inarm': bend_in_out3,
                'outarm': bend_in_out4,
                # 'heater': custom_elec_single(m1_taper_width=30, heater_length=wbg_length),
                # 'heater': custom_elec_single(m1_taper_width=10, heater_length=wbg_length),
            }

            insts_specs = [
                # i3.ConnectManhattan('bend90_ua:in', 'bend90_ud:out'),
                i3.Place('wbg:in', (0, 0)),
                # i3.PlaceRelative('heater:left_loc_of_heater', 'wbg:in', (35, 0)),
                i3.PlaceRelative('inarm:out', 'wbg:in', (0, 0)),
                i3.PlaceRelative('outarm:in', 'wbg:out', (0, 0)),
                i3.FlipV('outarm'),
            ]
            if self.heater_open:
                insts_insts['heater'] = custom_elec_single(m1_taper_width=10, heater_length=wbg_length)
                insts_specs.append(i3.PlaceRelative('heater:left_loc_of_heater', 'wbg:in', (35, 0)))

            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            ports += i3.expose_ports(self.instances,
                                     {
                                         'inarm:in': 'in',
                                         'outarm:out': 'out',
                                         # 'heater:elec1': 'elec2',
                                         # 'heater:elec2': 'elec1',
                                     })
            if self.heater_open:
                ports += i3.expose_ports(self.instances,
                                         {
                                             'heater:elec1': 'elec2',
                                             'heater:elec2': 'elec1',
                                         })
            return ports

class AMWBGwithArmScanField(i3.PCell):
    wbg_length = i3.PositiveNumberProperty(doc=" ", default=900.0)
    period = i3.PositiveNumberProperty(doc=" ", default=0.299)
    grating_width = i3.NonNegativeNumberProperty(doc=" ", default=0.163)
    apodization = i3.NonNegativeNumberProperty(doc="", default=200.0)
    apFunction = i3.StringProperty(default="Blackman", doc="type of waveguide: wide or narrow")
    apodization_type = i3.StringProperty(default='DoubleSide', doc="type of waveguide: wide or narrow")
    apodization_loc = i3.StringProperty(default='StartAndEnd', doc="type of waveguide: wide or narrow")
    textMarker = i3.BoolProperty(default=False, doc=".")
    heater_open = i3.BoolProperty(default='True', doc='False for no heater')
    EBL_scan_filed_length = i3.PositiveNumberProperty(default=1000, doc="EBL scan field length")
    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            wbg_length = self.wbg_length
            period = self.period
            grating_width = self.grating_width
            apodization = self.apodization
            apFunction = self.apFunction
            apodization_type = self.apodization_type
            apodization_loc = self.apodization_loc
            EBL_scan_filed_length = self.EBL_scan_filed_length
            delta_y = 140  # gap in vertical direction between two ports
            filterWBG = pdk.AMWBG(
                wbg_length=wbg_length,
                wbg_period=period,
                wbg_duty_cycle=0.5,
                wbg_grating_width=grating_width,
                wbg_grating_height=0.15,
                wbg_apodization_length=apodization,
                wbg_waveguide_width=1.,
                taper_length=25.,
                apodization_type=apodization_type,
                apodization_function=apFunction,
                apodization_loc=apodization_loc,
                to_draw_deltaL=False,
            )
            insts_insts = {
                'wbg': filterWBG,
                'inarm': bend_in_out,
                'outarm': bend_in_out,
                'temp_port': TempPort(),
                # 'heater': custom_elec_single(m1_taper_width=30, heater_length=wbg_length),
            }
            insts_specs = [
                # i3.ConnectManhattan('bend90_ua:in', 'bend90_ud:out'),
                i3.Place('inarm:in', (0, 0)),
                i3.PlaceRelative('wbg:in', 'inarm:out', (0, 0)),
                i3.PlaceRelative('outarm:in', 'wbg:out', (0, 0)),
                i3.PlaceRelative('temp_port:in', 'inarm:in', (EBL_scan_filed_length, -delta_y)),
                i3.ConnectManhattan([
                    ('temp_port:in', 'outarm:out'),
                ]),
            ]
            if self.heater_open:
                insts_insts['heater'] = custom_elec_single(m1_taper_width=10, heater_length=wbg_length)
                insts_specs.append(i3.PlaceRelative('heater:left_loc_of_heater', 'wbg:in', (35, 0)))
            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            ports += i3.expose_ports(self.instances,
                                     {
                                         'inarm:in': 'in',
                                         'temp_port:out': 'out',
                                     })
            if self.heater_open:
                ports += i3.expose_ports(self.instances,
                                         {
                                             'heater:elec1': 'elec2',
                                             'heater:elec2': 'elec1',
                                         })
            return ports


if __name__ == '__main__':
    # lo = AMWBGwithArmScanField(apFunction='Blackman',
    #                           apodization=300,
    #                           wbg_length=850,
    #                           apodization_type='DoubleSide',
    #                           heater_open=True,
    #                           name='AMWBGec')
    # lo.Layout().visualize(annotate=True)
    lo=AMWBGwithArm_sameside_reverse()
    lo.Layout().write_gdsii('AMWBGwithArm_sameside_reverse.gds')
