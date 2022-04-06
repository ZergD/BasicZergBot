from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.unit_typeid import UnitTypeId
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.units import Units
from sc2.unit import Unit
from pprint import pprint


class BasicZerg(BotAI):
    """
    Goal: zergling speed + (baneling all in #TODO To implement later)

    - build drones/overlords
    - build hatch
    - build gaz
    - build pool
    """

    def __init__(self):
        super(BasicZerg, self).__init__()
        self.first_expantion = False
        self.distance_to_closes_hatch = 99999
        self.position_of_first_expand = None
        self.expand_positions = []

    def display_debug_structure_data(self):
        for structure in self.structures:
            self._client.debug_text_world(
                "\n".join(
                    [
                        f"{structure.type_id.name}:{structure.type_id.value}",
                        f"({structure.position.x:.2f},{structure.position.y:.2f})",
                        f"{structure.build_progress:.2f}",
                    ] + [repr(x) for x in structure.orders]
                ),
                structure.position3d,
                color=(0, 255, 0),
                size=12,
            )

    async def on_step(self, iteration: int):
        # Debug part //
        print(f"step {iteration} : time: {self.time_formatted}")
        print(self.expand_positions)
        if iteration == 10:
            self.expand_positions.pop(0)
            print("############### ARRAY POPPED WTF ############################")

        self.display_debug_structure_data()

        # compute closest expand location
        if iteration == 1:
            distances = {}
            hq: Unit = self.townhalls.first
            print(f"position of hq = {hq.position}")
            for base in self.expansion_locations_list:
                res_distance = base.position.distance_to(hq.position)
                distances[res_distance] = base
                if res_distance < self.distance_to_closes_hatch and res_distance != 0:
                    self.distance_to_closes_hatch = res_distance
                    self.position_of_first_expand = base.position
                print(f"base position {base.position} is at distance: {self.distance_to_closes_hatch}")

            d = dict(sorted(distances.items()))
            for elem in d.keys():
                self.expand_positions.append(d[elem])
            # remove the first position as it is the same as starting base.
            _ = self.expand_positions.pop()
            pprint(d)
            print("--------- self.expand_positions: ")
            print(self.expand_positions)
            print(f"final expand position:     {self.position_of_first_expand}")
            print(f"position of first expand:  {self.expand_positions[0]}")
            print(f"position of second expand: {self.expand_positions[1]}")

        larvae: Units = self.larva
        forces: Units = self.units.of_type({UnitTypeId.ZERGLING})

        # If all our town-halls are dead, send all our units to attack
        if not self.townhalls:
            for unit in self.units.of_type(
                    {UnitTypeId.DRONE, UnitTypeId.QUEEN, UnitTypeId.ZERGLING}
            ):
                unit.attack(self.enemy_start_locations[0])
            return
        else:
            hq: Unit = self.townhalls.first

        # If supply is low, train Overlord
        if self.supply_left < 2 and \
                larvae and \
                self.can_afford(UnitTypeId.OVERLORD) and \
                not self.already_pending(UnitTypeId.OVERLORD):
            larvae.random.train(UnitTypeId.OVERLORD)

        # If worker supply < X, train Drones!
        if self.supply_workers + self.already_pending(UnitTypeId.DRONE) < 17:
            if larvae and self.can_afford(UnitTypeId.DRONE):
                larva: Unit = larvae.random
                larva.train(UnitTypeId.DRONE)

        # build first expantion
        if self.structures(UnitTypeId.HATCHERY).amount + self.already_pending(UnitTypeId.HATCHERY) < 3:
            if self.can_afford(UnitTypeId.HATCHERY):
                for drone in self.workers.collecting:
                    drone: Unit
                    drone.build(UnitTypeId.HATCHERY, self.expand_positions[0])
                self.expand_positions.pop(0)

        # Build spawing bool only after self.first_expantion == True
        if self.structures(UnitTypeId.SPAWNINGPOOL).amount + self.already_pending(UnitTypeId.SPAWNINGPOOL) == 0 and \
                self.first_expantion:
            if self.can_afford(UnitTypeId.SPAWNINGPOOL):
                await self.build(UnitTypeId.SPAWNINGPOOL, near=hq.position.towards(self.game_info.map_center, 5))

        print("----------------------------------------------------------------------------------")


def main():
    run_game(
        maps.get("Abyssal Reef LE"),
        [Bot(Race.Zerg, BasicZerg()),
         Computer(Race.Terran, Difficulty.Easy)],
        realtime=True,
    )


if __name__ == "__main__":
    main()
