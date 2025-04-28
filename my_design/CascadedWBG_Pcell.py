from si_fab import all as pdk
from ipkiss3 import all as i3
from si_fab.technology import TECH
from picazzo3.wg.bend import WgBend90
from GACDC_Pcell import GACDC_HT
from ECrow_Pcell import ECrow
from AMWBGwithArm_pcell import AMWBGwithArm, AMWBGwithArmScanField, AMWBGwithArm_sameside_reverse,AMWBGwithArm_sameside


class TempPort(i3.PCell):
    """
       in       ---------------------------------    out
    """
    class Layout(i3.LayoutView):
        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name="in", position=(0.0, 0.0), angle=180.0)
            ports += i3.OpticalPort(name="out", position=(0.0, 0.0), angle=0.0)
            return ports


class LongCascadedWBG(i3.PCell):
    num_WBG = i3.PositiveNumberProperty(doc="the number of unit WBG", default=3)
    gap_x = i3.NonNegativeNumberProperty(doc="horizontal gap between WBGs", default=0)
    gap_y = i3.NonNegativeNumberProperty(doc="vertical gap between WBGs", default=0)
    wbg_length = i3.PositiveNumberProperty(doc=" ", default=850.0)
    period = i3.PositiveNumberProperty(doc=" ", default=0.2965)
    grating_width = i3.NonNegativeNumberProperty(doc=" ", default=0.163)
    apodization = i3.NonNegativeNumberProperty(doc="", default=300.0)
    apFunction = i3.StringProperty(default="Blackman", doc="type of waveguide: wide or narrow")
    apodization_type = i3.StringProperty(default='DoubleSide', doc="type of waveguide: wide or narrow")
    apodization_loc = i3.StringProperty(default='StartAndEnd', doc="type of waveguide: wide or narrow")
    textMarker = i3.BoolProperty(default=False, doc=".")
    heater_open = i3.BoolProperty(default='True', doc='False for no heater')

    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            num_WBG = self.num_WBG
            gap_x = self.gap_x
            gap_y = self.gap_y
            wbg_length = self.wbg_length
            period = self.period
            grating_width = self.grating_width
            apodization = self.apodization
            apFunction = self.apFunction
            apodization_type = self.apodization_type
            apodization_loc = self.apodization_loc
            heater_open = self.heater_open
            sign = -1
            filterWBG = AMWBGwithArmScanField(apFunction=apFunction,
                                              period=period,
                                              apodization=apodization,
                                              wbg_length=wbg_length,
                                              apodization_type=apodization_type,
                                              heater_open=heater_open,
                                              name='AMWBGec')

            insts_insts = {}

            for i in range(int(num_WBG)):
                insts_insts['WBG_{}'.format(i)] = filterWBG

            insts_specs = [i3.Place("WBG_0:in", (0.0, 0.0))]
            for i in range(int(num_WBG)):
                insts_specs.append(i3.FlipV("WBG_{}".format(i)))
            for i in range(int(num_WBG) - 1):
                sign = -sign
                # if i % 2 == 0:
                insts_specs.append(
                    i3.PlaceRelative("WBG_{}:in".format(i + 1), "WBG_{}:out".format(i), (gap_x, sign * gap_y))
                )
                temp = i3.ConnectManhattan([
                        ("WBG_{}:in".format(i + 1), "WBG_{}:out".format(i))
                    ],
                        bend_radius=10
                    )
                insts_specs.append(temp)
            # insts_specs.append(i3.FlipV("WBG_0"))
            # insts_specs = [
            #     # i3.ConnectManhattan('bend90_ua:in', 'bend90_ud:out'),
            #     i3.Place('wbg:in', (0, 0)),
            #     # i3.PlaceRelative('heater:left_loc_of_heater', 'wbg:in', (35, 0)),
            #     i3.PlaceRelative('inarm:out', 'wbg:in', (0, 0)),
            #     i3.PlaceRelative('outarm:in', 'wbg:out', (0, 0)),
            # ]
            # if self.heater_open:
            #     insts_insts['heater'] = custom_elec_single(m1_taper_width=10, heater_length=wbg_length)
            #     insts_specs.append(i3.PlaceRelative('heater:left_loc_of_heater', 'wbg:in', (35, 0)))
            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            num_WBG = int(self.num_WBG)
            # optical ports
            ports += i3.expose_ports(self.instances,
                                     {
                                         "WBG_{}:in".format(0): 'in',
                                         "WBG_{}:out".format(num_WBG-1): 'out',
                                     })
            # electrical ports
            if self.heater_open:
                for i in range(num_WBG):
                    ports += i3.expose_ports(self.instances,
                                             {
                                                 "WBG_{}:elec1".format(i): 'elec_{}_1'.format(i+1),
                                                 "WBG_{}:elec2".format(i): 'elec_{}_2'.format(i+1),
                                             })
            return ports


class CompactCascadedWBG(i3.PCell):
    _name_prefix = "CompactCascadedWBG"
    num_WBG = i3.PositiveNumberProperty(doc="the number of unit WBG", default=4)
    gap_x = i3.PositiveNumberProperty(doc="horizontal gap between WBGs", default=40)
    gap_y = i3.PositiveNumberProperty(doc="vertical gap between WBGs", default=30)
    wbg_length = i3.PositiveNumberProperty(doc=" ", default=850.0)
    period = i3.PositiveNumberProperty(doc=" ", default=0.2965)
    grating_width = i3.NonNegativeNumberProperty(doc=" ", default=0.163)
    apodization = i3.NonNegativeNumberProperty(doc="", default=300.0)
    apFunction = i3.StringProperty(default="Blackman", doc="type of waveguide: wide or narrow")
    apodization_type = i3.StringProperty(default='DoubleSide', doc="type of waveguide: wide or narrow")
    apodization_loc = i3.StringProperty(default='StartAndEnd', doc="type of waveguide: wide or narrow")
    textMarker = i3.BoolProperty(default=False, doc=".")
    heater_open = i3.BoolProperty(default='True', doc='False for no heater')
    EBL_scan_filed_length = i3.PositiveNumberProperty(default=1000, doc="EBL scan field length")
    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            num_WBG = self.num_WBG
            gap_x = self.gap_x
            gap_y = self.gap_y
            wbg_length = self.wbg_length
            period = self.period
            grating_width = self.grating_width
            apodization = self.apodization
            apFunction = self.apFunction
            apodization_type = self.apodization_type
            apodization_loc = self.apodization_loc
            heater_open = self.heater_open
            EBL_scan_filed_length = self.EBL_scan_filed_length
            filterWBG = AMWBGwithArm_sameside(apFunction=apFunction,
                                      apodization=wbg_length / 2,
                                      wbg_length=wbg_length,
                                      period =period,
                                      apodization_type=apodization_type,
                                      heater_open=heater_open,
                                      grating_width=0,
                                      )
            filterWBG_reverse = AMWBGwithArm_sameside_reverse(apFunction=apFunction,
                                      apodization=wbg_length / 2,
                                      wbg_length=wbg_length,
                                      period =period,
                                      apodization_type=apodization_type,
                                      heater_open=heater_open,
                                      grating_width=0,
                                      )

            insts_insts = {}
            insts_insts['WBG_0'] = filterWBG_reverse
            insts_insts['WBG_1'] = filterWBG
            insts_insts['WBG_2'] = filterWBG_reverse
            insts_insts['WBG_3'] = filterWBG

            # for i in range(int(num_WBG)):
            #     insts_insts['WBG_{}'.format(i)] = filterWBG

            insts_insts['temp_port_left'] = TempPort()
            insts_insts['temp_port_right'] = TempPort()
            insts_specs = [i3.Place("temp_port_left:in", (0.0, 0.0))]
            insts_specs.append(
                i3.PlaceRelative('temp_port_right:in', "temp_port_left:in",
                                 (EBL_scan_filed_length * 4, 0)
            )
            )
            insts_specs.append(
                i3.PlaceRelative('WBG_0:in', "temp_port_left:in", (20, 0))
            )
            insts_specs.append(i3.FlipV('WBG_0'))
            insts_specs.append(
                i3.ConnectManhattan([
                    ('WBG_0:in', "temp_port_left:out"),
                ],
                    bend_radius=10
                )
            )
            for i in range(int(num_WBG) - 1):
                if (i % 2) == 0:
                    insts_specs.append(
                        i3.PlaceRelative("WBG_{}:in".format(i + 1), "WBG_{}:out".format(i), (gap_x - 5, 00)),
                    )
                    insts_specs.append(i3.FlipV('WBG_{}'.format(i + 1)))
                    insts_specs.append(
                        i3.ConnectManhattan([
                            ("WBG_{}:in".format(i + 1), "WBG_{}:out".format(i))
                        ],
                            bend_radius=10)
                    )
                if (i % 2) == 1:
                    insts_specs.append(i3.FlipV('WBG_{}'.format(i + 1)))
                    insts_specs.append(
                        i3.PlaceRelative("WBG_{}:in".format(i + 1), "WBG_{}:out".format(i), (gap_x - 5, 00))
                    )
                    insts_specs.append(i3.FlipV('WBG_{}'.format(i + 1)))
                    insts_specs.append(
                        i3.ConnectManhattan([
                                            ("WBG_{}:in".format(i + 1), "WBG_{}:out".format(i))
                                        ],
                                            bend_radius=10
                                        )
                    )
            # for i in range(int(num_WBG) - 1):
            #     if (i % 2) == 0:
            #         insts_specs.append(
            #             i3.PlaceRelative("WBG_{}:out".format(i + 1), "WBG_{}:out".format(i), (0, gap_y))
            #         )
            #         insts_specs.append(
            #             i3.ConnectManhattan([
            #                 ("WBG_{}:out".format(i + 1), "WBG_{}:out".format(i))
            #             ],
            #                 bend_radius=10
            #             )
            #         )
            #     if (i % 2) == 1:
            #         insts_specs.append(i3.FlipV('WBG_{}'.format(i + 1)))
            #         insts_specs.append(
            #             i3.PlaceRelative("WBG_{}:in".format(i + 1), "WBG_{}:in".format(i), (0, gap_y))
            #         )
            #         insts_specs.append(
            #             i3.ConnectManhattan([
            #                 ("WBG_{}:in".format(i + 1), "WBG_{}:in".format(i))
            #             ],
            #                 bend_radius=10
            #             )
            #         )
            if (int(num_WBG) % 2) == 0:
                insts_specs.append(
                    i3.ConnectManhattan([
                        ('temp_port_right:in', "WBG_{}:out".format(i + 1))
                    ],
                        bend_radius=10
                    )
                )
            if (int(num_WBG) % 2) == 1:
                insts_specs.append(
                    i3.ConnectManhattan([
                        ('temp_port_right:in', "WBG_{}:out".format(i + 1))
                    ],
                        bend_radius=10
                    )
                )
            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            num_WBG = int(self.num_WBG)
            # optical ports
            ports += i3.expose_ports(self.instances,
                                     {
                                         "temp_port_left:in": 'in',
                                         "temp_port_right:out": 'out',
                                     })
            # electrical ports
            if self.heater_open:
                for i in range(num_WBG):
                    # if i % 2 == 0:
                    ports += i3.expose_ports(self.instances,
                                             {
                                                 "WBG_{}:elec1".format(i): 'elec{}'.format((i * 2) + 1),
                                                 "WBG_{}:elec2".format(i): 'elec{}'.format((i * 2) + 2),
                                             })
                    # if i % 2 == 1:
                    #     ports += i3.expose_ports(self.instances,
                    #                              {
                    #                                  "WBG_{}:elec1".format(i): 'elec{}'.format(i+2),
                    #                                  "WBG_{}:elec2".format(i): 'elec{}'.format(i+1),
                    #                              })
            return ports

class CompactCascadedWBG_HV(i3.PCell):
    _name_prefix = "CompactCascadedWBG"
    num_WBG = i3.PositiveNumberProperty(doc="the number of unit WBG", default=4)
    gap_x = i3.PositiveNumberProperty(doc="horizontal gap between WBGs", default=100)
    gap_y = i3.PositiveNumberProperty(doc="vertical gap between WBGs", default=30)
    wbg_length = i3.PositiveNumberProperty(doc=" ", default=850.0)
    period = i3.PositiveNumberProperty(doc=" ", default=0.2965)
    grating_width = i3.NonNegativeNumberProperty(doc=" ", default=0.163)
    apodization = i3.NonNegativeNumberProperty(doc="", default=300.0)
    apFunction = i3.StringProperty(default="Blackman", doc="type of waveguide: wide or narrow")
    apodization_type = i3.StringProperty(default='DoubleSide', doc="type of waveguide: wide or narrow")
    apodization_loc = i3.StringProperty(default='StartAndEnd', doc="type of waveguide: wide or narrow")
    textMarker = i3.BoolProperty(default=False, doc=".")
    heater_open = i3.BoolProperty(default='True', doc='False for no heater')
    EBL_scan_filed_length = i3.PositiveNumberProperty(default=1000, doc="EBL scan field length")
    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            num_WBG = self.num_WBG
            gap_x = self.gap_x
            gap_y = self.gap_y
            wbg_length = self.wbg_length
            period = self.period
            grating_width = self.grating_width
            apodization = self.apodization
            apFunction = self.apFunction
            apodization_type = self.apodization_type
            apodization_loc = self.apodization_loc
            heater_open = self.heater_open
            EBL_scan_filed_length = self.EBL_scan_filed_length
            filterWBG = AMWBGwithArm_sameside(apFunction=apFunction,
                                      apodization=wbg_length / 2,
                                      wbg_length=wbg_length,
                                      period =period,
                                      apodization_type=apodization_type,
                                      heater_open=heater_open,
                                      grating_width=0,
                                      )
            filterWBG_reverse = AMWBGwithArm_sameside_reverse(apFunction=apFunction,
                                      apodization=wbg_length / 2,
                                      wbg_length=wbg_length,
                                      period =period,
                                      apodization_type=apodization_type,
                                      heater_open=heater_open,
                                      grating_width=0,
                                      )

            insts_insts = {}
            insts_insts['WBG_0'] = filterWBG
            insts_insts['WBG_1'] = filterWBG
            insts_insts['WBG_2'] = filterWBG
            insts_insts['WBG_3'] = filterWBG_reverse

            # for i in range(int(num_WBG)):
            #     insts_insts['WBG_{}'.format(i)] = filterWBG

            insts_insts['temp_port_left'] = TempPort()
            insts_insts['temp_port_right'] = TempPort()
            insts_specs = [i3.Place("temp_port_left:in", (0.0, 0.0))]
            insts_specs.append(
                i3.PlaceRelative('temp_port_right:in', "temp_port_left:in",
                                 (EBL_scan_filed_length * 4, 0)
            )
            )
            insts_specs.append(
                i3.PlaceRelative('WBG_0:in', "temp_port_left:in", (30, -30),angle=90)
            )
            insts_specs.append(i3.FlipV('WBG_0'))
            insts_specs.append(
                i3.ConnectManhattan([
                    ('WBG_0:in', "temp_port_left:out"),
                ],
                    bend_radius=10
                )
            )
            for i in range(int(num_WBG) - 1):
                if i==0:
                    insts_specs.append(
                        i3.PlaceRelative("WBG_{}:in".format(i + 1), "WBG_{}:out".format(i), (20, -gap_x )),
                    )
                    insts_specs.append(i3.FlipV('WBG_{}'.format(i + 1)))
                    insts_specs.append(
                        i3.ConnectManhattan([
                            ("WBG_{}:in".format(i + 1), "WBG_{}:out".format(i))
                        ],
                            bend_radius=10)
                    )
                if i==2:
                    insts_specs.append(
                        i3.PlaceRelative("WBG_{}:in".format(i + 1), "WBG_{}:out".format(i), (100, gap_x )),
                    )
                    insts_specs.append(i3.FlipV('WBG_{}'.format(i + 1)))
                    insts_specs.append(
                        i3.ConnectManhattan([
                            ("WBG_{}:in".format(i + 1), "WBG_{}:out".format(i))
                        ],
                            bend_radius=10)
                    )
                if i==3:
                    insts_specs.append(i3.FlipV('WBG_{}'.format(i + 1)))
                    insts_specs.append(
                        i3.PlaceRelative("WBG_{}:in".format(i + 1), "WBG_{}:out".format(i), (20, 100 ),angle=-90)
                    )
                    insts_specs.append(i3.FlipV('WBG_{}'.format(i + 1)))
                    insts_specs.append(
                        i3.ConnectManhattan([
                                            ("WBG_{}:in".format(i + 1), "WBG_{}:out".format(i))
                                        ],
                                            bend_radius=10
                                        )
                    )
                if i == 1:
                    insts_specs.append(i3.FlipV('WBG_{}'.format(i + 1)))
                    insts_specs.append(
                        i3.PlaceRelative("WBG_{}:in".format(i + 1), "WBG_{}:out".format(i), (-100, 100 ),angle=-90)
                    )
                    insts_specs.append(i3.FlipV('WBG_{}'.format(i + 1)))
                    insts_specs.append(
                        i3.ConnectManhattan([
                                            ("WBG_{}:in".format(i + 1), "WBG_{}:out".format(i))
                                        ],
                                            bend_radius=10
                                        )
                    )

            # for i in range(int(num_WBG) - 1):
            #     if (i % 2) == 0:
            #         insts_specs.append(
            #             i3.PlaceRelative("WBG_{}:out".format(i + 1), "WBG_{}:out".format(i), (0, gap_y))
            #         )
            #         insts_specs.append(
            #             i3.ConnectManhattan([
            #                 ("WBG_{}:out".format(i + 1), "WBG_{}:out".format(i))
            #             ],
            #                 bend_radius=10
            #             )
            #         )
            #     if (i % 2) == 1:
            #         insts_specs.append(i3.FlipV('WBG_{}'.format(i + 1)))
            #         insts_specs.append(
            #             i3.PlaceRelative("WBG_{}:in".format(i + 1), "WBG_{}:in".format(i), (0, gap_y))
            #         )
            #         insts_specs.append(
            #             i3.ConnectManhattan([
            #                 ("WBG_{}:in".format(i + 1), "WBG_{}:in".format(i))
            #             ],
            #                 bend_radius=10
            #             )
            #         )
            if (int(num_WBG) % 2) == 0:
                insts_specs.append(
                    i3.ConnectManhattan([
                        ('temp_port_right:in', "WBG_{}:out".format(i + 1))
                    ],
                        bend_radius=10
                    )
                )
            if (int(num_WBG) % 2) == 1:
                insts_specs.append(
                    i3.ConnectManhattan([
                        ('temp_port_right:in', "WBG_{}:out".format(i + 1))
                    ],
                        bend_radius=10
                    )
                )
            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            num_WBG = int(self.num_WBG)
            # optical ports
            ports += i3.expose_ports(self.instances,
                                     {
                                         "temp_port_left:in": 'in',
                                         "temp_port_right:out": 'out',
                                     })
            # electrical ports
            if self.heater_open:
                for i in range(num_WBG):
                    # if i % 2 == 0:
                    ports += i3.expose_ports(self.instances,
                                             {
                                                 "WBG_{}:elec1".format(i): 'elec{}'.format((i * 2) + 1),
                                                 "WBG_{}:elec2".format(i): 'elec{}'.format((i * 2) + 2),
                                             })
                    # if i % 2 == 1:
                    #     ports += i3.expose_ports(self.instances,
                    #                              {
                    #                                  "WBG_{}:elec1".format(i): 'elec{}'.format(i+2),
                    #                                  "WBG_{}:elec2".format(i): 'elec{}'.format(i+1),
                    #                              })
            return ports

if __name__ == '__main__':
    # lo = LongCascadedWBG()
    lo = CompactCascadedWBG_HV(wbg_length=900)
    # lo.Layout().visualize(annotate=True)
    lo.Layout().write_gdsii('CompactCascadedWBG_HV.gds')
