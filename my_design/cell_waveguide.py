from si_fab import all as pdk
from ipkiss3 import all as i3
from si_fab.technology import TECH


class customTaper(i3.PCell):
    _name_prefix = "customTaper"
    taperW1 = i3.PositiveNumberProperty(default=0.45, doc="taperW1.")
    taperW2 = i3.PositiveNumberProperty(default=3., doc="taperW2.")
    taperLength = i3.PositiveNumberProperty(default=100., doc="taperLength.")
    trace_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )

    class Layout(i3.LayoutView):

        def _generate_elements(self, elems):
            taperW1 = self.taperW1
            taperW2 = self.taperW2
            taperLength = self.taperLength
            core = self.trace_template.core_layer
            cladding = self.trace_template.cladding_layer

            elems_to_merge_core = [i3.Wedge(
                layer=core,
                begin_coord=(0, 0),
                end_coord=(taperLength, 0.),
                begin_width=taperW1,
                end_width=taperW2,
            )]
            elems += i3.merge_elements(elems_to_merge_core, core)

            elems_to_merge_cladding = [i3.Wedge(
                layer=cladding,
                begin_coord=(0, 0),
                end_coord=(taperLength, 0.),
                begin_width=taperW1 + 7,
                end_width=taperW2 + 7,
            )]
            elems += i3.merge_elements(elems_to_merge_cladding, cladding)
            return elems

        def _generate_ports(self, ports):
            taperLength = self.taperLength
            ports += i3.OpticalPort(name='in', position=(0., 0.), angle=180.0)
            ports += i3.OpticalPort(name='out', position=(taperLength, 0.0), angle=0.0)
            return ports


class customWavegudie(i3.PCell):
    _name_prefix = "customWavegudie"
    n_o_waveguide = i3.IntProperty(default=12, doc="number of waveguide")
    Length = i3.PositiveNumberProperty(default=800, doc="waveguide length.")
    Width1 = i3.PositiveNumberProperty(default=0.45, doc="narrow width.")
    Width2 = i3.PositiveNumberProperty(default=0.45, doc="wide width.")
    taperLength = i3.PositiveNumberProperty(default=90./2, doc="taperLength.")
    bendRadius = i3.PositiveNumberProperty(default=20., doc="bendRadius.")
    gapBetweenWg = i3.PositiveNumberProperty(default=50., doc="gapBetweenWg.")
    # rounding_algorithm = i3.DefinitionProperty(default=None, doc="rounding_algorithm.")
    trace_template = i3.TraceTemplateProperty(
        default=pdk.SiWireWaveguideTemplate(),
        doc="Trace template of the access waveguide"
    )

    # gap = i3.PositiveNumberProperty(default=10., doc="gap between GC output and the input port of devices.")
    # taperW2 = i3.PositiveNumberProperty(default=3., doc="taperW2.")
    # taperLength = i3.PositiveNumberProperty(default=100., doc="taperLength.")

    class Layout(i3.LayoutView):
        def _generate_elements(self, elems):
            n_o_waveguide = self.n_o_waveguide
            Length = self.Length
            Width1 = self.Width1
            Width2 = self.Width2
            taperLength = self.taperLength
            bendRadius = self.bendRadius
            gapBetweenWg = self.gapBetweenWg
            core = self.trace_template.core_layer
            cladding = self.trace_template.cladding_layer

            elems_to_merge_core = []
            elems_to_merge_cladding = []
            # WgBend90
            for i in range(int(n_o_waveguide)):
                elems_to_merge_core.append(
                    i3.Rectangle(layer=core,
                                 center=(taperLength + Length / 2, gapBetweenWg * i),
                                 # box_size=(Width2, Length))
                                 box_size=(Length, Width2))
                )
                elems_to_merge_cladding.append(
                    i3.Rectangle(layer=cladding,
                                 center=(taperLength + Length / 2, gapBetweenWg * i),
                                 box_size=(Length, Width2 + 7))
                )
            elems += i3.merge_elements(elems_to_merge_core, core)
            elems += i3.merge_elements(elems_to_merge_cladding, cladding)
            return elems

        def _generate_instances(self, insts):
            # gap = self.gap
            # gcc32 = pdk.GCrow()
            n_o_waveguide = self.n_o_waveguide
            bendRadius = self.bendRadius
            Length = self.Length
            taperLength = self.taperLength
            gapBetweenWg = self.gapBetweenWg
            trace_template = self.trace_template
            # rounding_algorithm = self.rounding_algorithm
            taper = customTaper(
                taperW1=self.Width1,
                taperW2=self.Width2,
                taperLength=self.taperLength,
            )

            insts_insts = dict()
            insts_specs = list()
            for i in range(int(n_o_waveguide)):
                insts_insts[f'taper{i}_L'] = taper
                insts_specs.append(
                    i3.Place(f'taper{i}_L:in', (0.0, gapBetweenWg*i))
                )

                insts_insts[f'taper{i}_R'] = taper
                insts_specs.append(
                    i3.Place(f'taper{i}_R:out', (taperLength+Length, gapBetweenWg * i), angle=180.)
                )

            if int(n_o_waveguide) != 1:
                # if int(n_o_waveguide) % 2 == 0:
                for i in range(int(n_o_waveguide)):
                    if i >= int(n_o_waveguide)-1:
                        break
                    else:
                        if i % 2 == 0:
                            insts_specs.append(
                                i3.ConnectManhattan(f'taper{i}_R:in', f'taper{i+1}_R:in',
                                                    bend_radius=bendRadius,
                                                    # control_points=control_points,
                                                    # rounding_algorithm=rounding_algorithm,
                                                    )
                            )
                        else:
                            insts_specs.append(
                                i3.ConnectManhattan(f'taper{i}_L:in', f'taper{i + 1}_L:in',
                                                    bend_radius=bendRadius,
                                                    # control_points=control_points,
                                                    # rounding_algorithm=rounding_algorithm,
                                                    )
                            )

            # insts_insts = {
            #     "taper": taper,
            # }
            # insts_specs = [
            #     i3.Place("taper:in", (0.0, 0.0)),
            # ]
            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            taperLength = self.taperLength
            n_o_waveguide = self.n_o_waveguide
            gapBetweenWg = self.gapBetweenWg
            Length = self.Length
            bendRadius = self.bendRadius
            ports += i3.OpticalPort(name='in', position=(0., 0.), angle=180.0)
            if int(n_o_waveguide)%2 == 0:
                ports += i3.OpticalPort(name='out', position=(0., gapBetweenWg*(int(n_o_waveguide)-1)), angle=180.0)
            else:
                ports += i3.OpticalPort(name='out', position=(taperLength*2 + Length, gapBetweenWg*(int(n_o_waveguide)-1)), angle=0.0)

            return ports

if __name__ == '__main__':
    # WBG1 = custom_amwbg(apodization=30, wbg_length=100, period=0.3, grating_width=0.16)
    #
    # lo = WBG1
    lo = customWavegudie()
    lo.Layout().visualize(annotate=True)
    lo.Layout().write_gdsii('customWavegudie.gds')

    a = lo.Layout().instances
    insts_dic = a
    totallength = 0
    for instance in insts_dic:
        if "_to_" in instance:
            print("This is the connector's instance. Print the length below.")
            totallength += insts_dic[instance].reference.trace_length()
            print("{} length is {}:".format(instance, totallength))

    totallength += lo.n_o_waveguide * (lo.Length + lo.taperLength * 2)
    print(f'totallength {totallength}')
