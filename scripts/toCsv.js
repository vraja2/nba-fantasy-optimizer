var fs = require('fs');

stats = JSON.parse(fs.readFileSync("../data/seasonStats.json").toString());

var statNames = {};
Object.keys(stats).forEach(function (yearKey) {
  Object.keys(stats[yearKey]).forEach(function (playerKey) {
    Object.keys(stats[yearKey][playerKey]).forEach(function (statType) {
      Object.keys(stats[yearKey][playerKey][statType]).forEach(function (statName) {
        statNames[statType] = (statNames[statType] || {});
        statNames[statType][statName] = true;
      });
    });
  });
});

var table = [];
Object.keys(stats).forEach(function (yearKey) {
  Object.keys(stats[yearKey]).forEach(function (playerKey) {
    var player = {}
    player["year"] = yearKey;
    player["player"] = playerKey;
    Object.keys(stats[yearKey][playerKey]).forEach(function (statType) {
      Object.keys(statNames[statType]).forEach(function (statName) {
        player[statType + "-" + statName] = (stats[yearKey][playerKey][statType][statName] || "");
      });
    });
    table.push(player);
  });
});

var keyNames = Object.keys(table[0]);
var finalTable = [];
finalTable.push(keyNames);
finalTable = finalTable.concat(table.map(function (player) {
  return keyNames.map(function (keyName) {
    return player[keyName];
  });
}));

finalTable.forEach(function (row) {
  console.log(row.join(","));
});