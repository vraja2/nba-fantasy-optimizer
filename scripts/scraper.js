var fs = require('fs');
var request = require('request');
var cheerio = require('cheerio');
var async = require('async');

var YEARS = [1976, 1977, 1978, 1979, 1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015];

var STATS_TITLES = ["totals", "per_game", "per_minute", "per_poss", "advanced"];

function getSeasonStatsURL (year, statTitle) {
  return "http://www.basketball-reference.com/leagues/NBA_" + year + "_" + statTitle + ".html"
}

function parseTable($, rows) {
	var columnTitles = [];
	var table = [];

  rows.each(function (i, row) {
    if (i === 0) {
	    var columns = $(row).children();
			columns.each(function (i, el) {
				var columnVal = $(el).text();
				columnTitles.push(columnVal);
			});
		} else {
	    var columns = $(row).children();
			var rowObj = {};
			columns.each(function (i, el) {
				var columnVal = $(el).text();
			  var columnKey = columnTitles[i];
				rowObj[columnKey] = columnVal;
				table.push(rowObj);
			});
		}
	});

	return table;
}

var seasonStats = {};
var requests = [];

YEARS.forEach(function (year) {
	STATS_TITLES.forEach(function (statTitle) {
	  seasonStatsURL = getSeasonStatsURL(year, statTitle);

	  requests.push(function (cb) {
  		request(seasonStatsURL, function (error, response, html) {
  	    if (!error) {
  	      var $ = cheerio.load(html);

  				var rows = $(".stats_table tr");
  				var table = parseTable($, rows);

  				table.forEach(function (rowObj) {
  					var playerName = rowObj.Player;
  					delete rowObj.Player;
  					seasonStats[year] = (seasonStats[year] || {});
  					seasonStats[year][playerName] = (seasonStats[year][playerName] || {});
  					seasonStats[year][playerName][statTitle] = (seasonStats[year][playerName][statTitle] || {});

  					if (
  						seasonStats[year][playerName][statTitle].Tm !== "TOT" &&
  						playerName !== "Player"
  					) {
  						seasonStats[year][playerName][statTitle] = rowObj;
  					}
  				});
  			} else {
  				console.log(error);
  			}

  			console.log("Finished " + year + " " + statTitle);
  			cb();
  		});
	  });
	});
});

async.series(requests, function () {
	fs.writeFileSync("seasonStats.json", JSON.stringify(seasonStats));
});