from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.units import Units
from sc2.unit import Unit
from pprint import pprint
from sc2.position import Point2

import random


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
        # self.first_expantion = False
        self.distance_to_closes_hatch = 99999
        self.position_of_first_expand = None
        self.expand_positions = []
        self.zergling_speed = False

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

    def select_target(self) -> Point2:
        if self.enemy_structures:
            return random.choice(self.enemy_structures).position
        return self.enemy_start_locations[0]

    async def on_step(self, iteration: int):
        # Debug part //
        print(f"step {iteration} : time: {self.time_formatted}")
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

        # build first and second expantion
        if self.structures(UnitTypeId.HATCHERY).amount + self.already_pending(UnitTypeId.HATCHERY) < 3:
            if self.can_afford(UnitTypeId.HATCHERY):
                for drone in self.workers.collecting:
                    drone: Unit
                    drone.build(UnitTypeId.HATCHERY, self.expand_positions[0])
                self.expand_positions.pop(0)

        # Build spawing bool only after self.first_expantion == True
        if self.structures(UnitTypeId.SPAWNINGPOOL).amount + self.already_pending(UnitTypeId.SPAWNINGPOOL) == 0 and \
                self.structures(UnitTypeId.HATCHERY).amount == 2:
            if self.can_afford(UnitTypeId.SPAWNINGPOOL):
                await self.build(UnitTypeId.SPAWNINGPOOL, near=hq.position.towards(self.game_info.map_center, 5))

        if (
                self.structures(UnitTypeId.SPAWNINGPOOL)
                and self.gas_buildings.amount + self.already_pending(UnitTypeId.EXTRACTOR) < 2
        ):
            if self.can_afford(UnitTypeId.EXTRACTOR):
                # Can crash if we dont have any drones
                for vg in self.vespene_geyser.closer_than(10, hq):
                    drone: Unit = self.workers.random
                    drone.build_gas(vg)
                    break

        # saturate gas
        for g in self.gas_buildings:
            if g.assigned_harvesters < g.ideal_harvesters:
                w: Units = self.workers.closer_than(10, g)
                if w:
                    w.random.gather(g)

        # prod zerglings.
        if self.structures(UnitTypeId.SPAWNINGPOOL).ready:
            if larvae and self.can_afford(UnitTypeId.ZERGLING):
                larvae.random.train(UnitTypeId.ZERGLING)

        # research zergling speed
        if self.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED) == 0 \
                and self.can_afford(UpgradeId.ZERGLINGMOVEMENTSPEED):
            spawning_pool_ready: Units = self.structures(UnitTypeId.SPAWNINGPOOL).ready
            if spawning_pool_ready:
                self.research(UpgradeId.ZERGLINGMOVEMENTSPEED)

        # step 840 : time: 05:00
        # step 600 : time: 03:34, we can do it way earlier. This is ~grosso modo when speed finished.
        # but do we have enough lings ?
        if iteration == 840:
            # Attack enemy
            for unit in self.units.of_type({UnitTypeId.ZERGLING}):
                unit.attack(self.select_target())

        print("----------------------------------------------------------------------------------")


def main():
    run_game(
        maps.get("Abyssal Reef LE"),
        [Bot(Race.Zerg, BasicZerg()),
         Computer(Race.Terran, Difficulty.Medium)],
        realtime=True,
    )


if __name__ == "__main__":
    main()
