from ipkiss3 import all as i3
from si_fab import all as pdk


class Direction_coupler_90_10(i3.Circuit):
    """90:10 directional coupler"""
    wg1_length = i3.PositiveNumberProperty(default=27.0, doc="waveguide length.")
    wg2_length = i3.PositiveNumberProperty(default=10.0, doc="coupler length.")
    begin_position = i3.PositiveNumberProperty(default=5.0, doc="wg2 begins from wg1 end with begin position")
    gap1 = i3.PositiveNumberProperty(default=0.75, doc="coupling gap")
    gap2 = i3.PositiveNumberProperty(default=4.75, doc="waveguide gap")
    connect_wg_length = i3.PositiveNumberProperty(default=5.0, doc="input/output waveguide length")

    def _default_insts(self):
        insts = {}
        wg = pdk.SiWireWaveguideTemplate()
        wg.Layout(core_width=0.45, cladding_width=0.45 + 7)
        point1 = [(0.0, 0.0), (self.wg1_length + self.connect_wg_length, 0.0)]
        wg1 = i3.RoundedWaveguide(trace_template=wg)
        wg1.Layout(shape=point1)
        insts["wg_0"] = wg1

        point2 = [(0.0, 0.0), (self.wg2_length, 0.0)]
        wg2 = i3.RoundedWaveguide(trace_template=wg)
        wg2.Layout(shape=point2)
        insts["wg_1"] = wg2

        point3 = [(0.0, 0.0), (self.connect_wg_length, 0.0)]
        wg3 = i3.RoundedWaveguide(trace_template=wg)
        wg3.Layout(shape=point3)
        insts["wg_2"] = wg3

        # for i in range(4):
        #     wg = pdk.SiWireWaveguideTemplate()
        #     wg.Layout(core_width=0.45, cladding_width=0.45 + 7)
        #     wg1 = i3.RoundedWaveguide(trace_template=wg)
        #     point = [(-self.connect_wg_length, 0.0), (0.0, 0.0)]
        #     # if i < 2:
        #     #     point = [(points[i][0] - self.connect_wg_length, points[i][1]), (points[i][0], points[i][1])]
        #     # else:
        #     #     point = [(points[i][0], points[i][1]), (points[i][0] + self.connect_wg_length, points[i][1])]
        #     wg1.Layout(shape=point)
        #     insts["wg_{}".format(i)] = wg1

        return insts

    def _default_specs(self):
        specs = []
        points = [(0.0, 0.0), (self.begin_position, self.gap1), (self.wg1_length, 0.0), (self.wg1_length, self.gap2)]
        specs.append(i3.Place("wg_0:in", points[0], angle=180))
        specs.append(i3.Place("wg_1:in", points[1], angle=180))
        specs.append(i3.Place("wg_2:in", points[3], angle=180))
        # control_points = [(self.begin_position + self.wg2_length, self.gap1), (self.wg1_length, self.gap2)]
        specs.append(
            i3.ConnectBend(
                "wg_1:out",
                "wg_2:in",
                bend_radius=10,
            )
        )
        return specs

    def _default_exposed_ports(self):
        exposed_ports = {
            "wg_0:in": "in",
            # "wg_1:in": "in2",
            "wg_0:out": "out90",
            "wg_2:out": "out10",
        }
        return exposed_ports


if __name__ == '__main__':
    # pass
    # lo = IntegratedSource()
    # lo = CompactIntegratedSource()
    lo = Direction_coupler_90_10()
    # lo = GACDCPhaseShiftApodized(grating_period=0.3271)
    # lo = GACDC_HT(grating_period=0.3271)

    lo.Layout().visualize(annotate=True)
    lo.Layout().write_gdsii('Direction_coupler_90_10.gds')
