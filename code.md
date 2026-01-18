# Summary

Objective: Better Combat weapon_attributes generator, that can read existing weapon_attributes from files, modify them, and save (as) at ease.

Function:

1. Read existing weapon_attributes [examples can be found in data/bettercombat/weapon_attributes](https://github.com/ZsoltMolnarrr/BetterCombat/tree/1.21.1/common/src/main/resources/data/bettercombat/weapon_attributes), json format
2. Modify attributes of the json at will that follows the weapon_attributes parameter. These include pose, range_bonus(also depreciated, attack_range), two_handed, category, and attacks. It should also include better combat extension's two_handed_pose and the other stuff in attacks. [better combat extension docs](https://github.com/TheRedBrain/bettercombat-extension), [better combat weapon_attributes docs](https://github.com/ZsoltMolnarrr/BetterCombat/blob/1.21.11/common/src/main/java/net/bettercombat/api/WeaponAttributes.java)
3. Ability to add/modify/remove/change orders of attack attribute of the json
4. Save/Save as new file etc, json format
5. have a separate config storage of available weapon pose(pose of two_handed and other pose animations, used in choosing pose and two_handed pose exclusively)/attack animation preset(attack animation with predetermined attack direction, angle and other attack attributes)/sound(used in attack attribute swinging sounds) and other things if need be
6. if possible, also add a "update config" button so that the currently read json having a different attack animation/pose it will automatically write into the existing config making easy to update

GUI:

1. On top, should show currently editing file name. if currently creating new file leave empty
2. as well as file name it should house all info of the current json that isn't attacks, such as range_bonus, category, pose, offhand_pose, two_handed, etc. these can be edited by clicking it and rewriting the names, and for pose/two_handed_pose it shows a available weapon pose as a dropdown menu that you can select.
3. attack attribute section: fold-down stack that shows attack animation name by default. when opened(each attack indivually can be opened and closed) it shows the information of the attack, with hitbox, damage_multiplier, angle, upswing, attack range multiplier, movement speed multiplier, attack speed multiplier(better combat extension stuff), animation(shows attack animation preset when trying to select it and can be selected there to automatically assign values), swing_sound(has id and pitch inside), trail_particles(seeing no documentation so uhhh sorry). these stack can be also dragged over oneanother to change the order of the attack string.(if you drag the 4th attack between the 1st/2nd the 4th attack will move to the 2nd place and 2nd attack moves to 3rd, etc etc)
4. for ease of modifying attack_attribute, add a add new attack button as well. delete can be handled by selecting one of the attacks and have a trashcan icon or something(or just put a delete selected attack button)
5. SAVE button to save the attack json as well as save as so i can save as different json as well
6. (OPTIONAL) on the left you can see the selected pose of the json, as well as a play button that plays the attack combo on a single hand weapon situation. this does not include like dual wielding, offhand only and etc stuff but it SHOULD be better than going in blind.
