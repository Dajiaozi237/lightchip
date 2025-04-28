from si_fab import all as pdk
from ipkiss3 import all as i3
from broadband_filters import Broad_WidthChirp_GuassApodized,Broad_WidthChirp_GuassApodized_HT
from cell_ringDoubleBus import Ring_doubleBus
import numpy as np
TECH = pdk.TECH
class custom_elec_single(i3.PCell):
    _name_prefix = "custom_elec"
    heater_width = i3.PositiveNumberProperty(default=3., doc="Width of the heater")
    heater_length = i3.PositiveNumberProperty(default=55., doc="heater_length")
    m1_taper_width = i3.PositiveNumberProperty(default=25., doc="Width of the M1 contact")
    m1_taper_length = i3.PositiveNumberProperty(default=25., doc="Length of the M1 contacst")
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
class BFGC(i3.PCell):
    _name_prefix = "col"
    gap = i3.PositiveNumberProperty(default=110., doc="gap between grating coupler and device.")
    gap_y = i3.PositiveNumberProperty(default=150., doc="gap between grating coupler and device.")
    apodization = i3.NonNegativeNumberProperty(doc="", default=300.0)
    apFunction = i3.StringProperty(default="Blackman", doc="type of waveguide: wide or narrow")
    apodization_type = i3.StringProperty(default='DoubleSide', doc="type of waveguide: wide or narrow")
    wbg_length = i3.PositiveNumberProperty(doc=" ", default=850.0)
    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            gap = self.gap
            gap_y = self.gap_y
            apodization = self.apodization
            apFunction = self.apFunction
            apodization_type = self.apodization_type
            wbg_length = self.wbg_length
            gcc32 = pdk.GCrow()
            num_GACDC=6
            insts_insts = {
                "FA": gcc32,
                "BF1":Broad_WidthChirp_GuassApodized_HT(grating_period=0.32,
                                                                     gap=0.1,
                                                                     grating_width_drop_waveguide=0.16,
                                                                     grating_width_bus_waveguide=0.14,
                                                                     ),
                "BF2": Broad_WidthChirp_GuassApodized_HT(grating_period=0.325,
                                                                      gap=0.1,
                                                                      grating_width_drop_waveguide=0.16,
                                                                      grating_width_bus_waveguide=0.14,
                                                                      ),
                "BF3": Broad_WidthChirp_GuassApodized_HT(grating_period=0.33,
                                                                      gap=0.1,
                                                                      grating_width_drop_waveguide=0.16,
                                                                      grating_width_bus_waveguide=0.14,
                                                                      ),
                "BF4": Broad_WidthChirp_GuassApodized_HT(grating_period=0.335,
                                                                      gap=0.1,
                                                                      grating_width_drop_waveguide=0.16,
                                                                      grating_width_bus_waveguide=0.14,
                                                                      ),
                "BF5": Broad_WidthChirp_GuassApodized_HT(grating_period=0.32,
                                                                      gap=0.1,
                                                                      grating_width_drop_waveguide=0.14,
                                                                      grating_width_bus_waveguide=0.1,
                                                                      ),
                "BF6": Broad_WidthChirp_GuassApodized_HT(grating_period=0.32,
                                                                      gap=0.08,
                                                                      grating_width_drop_waveguide=0.14,
                                                                      grating_width_bus_waveguide=0.1,
                                                                      ),
                "BF7": Broad_WidthChirp_GuassApodized_HT(grating_period=0.32,
                                                                     gap=0.08,
                                                                     grating_width_drop_waveguide=0.14,
                                                                     grating_width_bus_waveguide=0.1,
                                                                     ),
                "BF8": Broad_WidthChirp_GuassApodized_HT(grating_period=0.32,
                                                                      gap=0.1,
                                                                      grating_width_drop_waveguide=0.14,
                                                                      grating_width_bus_waveguide=0.1,
                                                                      ),
                "BF9": Broad_WidthChirp_GuassApodized_HT(grating_period=0.33,
                                                                      gap=0.08,
                                                                      grating_width_drop_waveguide=0.14,
                                                                      grating_width_bus_waveguide=0.1,
                                                                      ),
                "BF10": Broad_WidthChirp_GuassApodized_HT(grating_period=0.34,
                                                                      gap=0.08,
                                                                      grating_width_drop_waveguide=0.14,
                                                                      grating_width_bus_waveguide=0.1,
                                                                     ),
            }
            insts_specs = [
                i3.Place("FA:wg_1", (0.0, 0.0)),

                i3.PlaceRelative('BF1:in', 'FA:wg_2', (gap, 0)),
                i3.PlaceRelative('BF2:in', 'FA:wg_5', (gap, 0)),
                i3.PlaceRelative('BF3:in', 'FA:wg_8', (gap, 0)),
                i3.PlaceRelative('BF4:in', 'FA:wg_11', (gap, 0)),
                i3.PlaceRelative('BF5:in', 'FA:wg_14', (gap, 0)),

                i3.PlaceRelative('BF6:in', 'FA:wg_17', (gap , 0)),
                i3.PlaceRelative('BF7:in', 'FA:wg_20', (gap , 0)),
                i3.PlaceRelative('BF8:in', 'FA:wg_23', (gap , 0)),
                i3.PlaceRelative('BF9:in', 'FA:wg_26', (gap , 0)),
                i3.PlaceRelative('BF10:in', 'FA:wg_29', (gap , 0)),

                i3.ConnectManhattan([
                    ('BF1:in', 'FA:wg_2'),
                    ('BF2:in', 'FA:wg_5'),
                    ('BF3:in', 'FA:wg_8'),
                    ('BF4:in', 'FA:wg_11'),
                    ('BF5:in', 'FA:wg_14'),
                    ('BF6:in', 'FA:wg_17'),
                    ('BF7:in', 'FA:wg_20'),
                    ('BF8:in', 'FA:wg_23'),
                    ('BF9:in', 'FA:wg_26'),
                    ('BF10:in', 'FA:wg_29'),
                ],
                ),
                i3.ConnectManhattan([
                    ('BF1:drop', 'FA:wg_3'),
                    ('BF2:drop', 'FA:wg_6'),
                    ('BF3:drop', 'FA:wg_9'),
                    ('BF4:drop', 'FA:wg_12'),
                    ('BF5:drop', 'FA:wg_15'),
                    ('BF6:drop', 'FA:wg_18'),
                    ('BF7:drop', 'FA:wg_21'),
                    ('BF8:drop', 'FA:wg_24'),
                    ('BF9:drop', 'FA:wg_27'),
                    ('BF10:drop', 'FA:wg_30'),
                ],
                ),
                i3.ConnectManhattan([
                    ('BF1:through', 'FA:wg_4'),
                    ('BF2:through', 'FA:wg_7'),
                    ('BF3:through', 'FA:wg_10'),
                    ('BF4:through', 'FA:wg_13'),
                    ('BF5:through', 'FA:wg_16'),
                    ('BF6:through', 'FA:wg_19'),
                    ('BF7:through', 'FA:wg_22'),
                    ('BF8:through', 'FA:wg_25'),
                    ('BF9:through', 'FA:wg_28'),
                    ('BF10:through', 'FA:wg_31'),
                ],
                ),
            ]
            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts
        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name="origin", position=(0.0, 0.0), angle=180.0)
if __name__ == '__main__':
                lo = BFGC()
                # lo.Layout().visualize(annotate=True)
                lo.Layout().write_gdsii('BFGC.gds')

