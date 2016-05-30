/**
 * Created by quek on 9/10/2014.
 */

var data; // a global










d3.json("out.json", function(error, json) {
    if (error) return console.warn(error);


    data = json;
    var selections = Object.keys(data)
    var default_selection = selections[0];

    visualPlot(default_selection);
    constructToolBar();
    generateSampleList(data);



});

Array.prototype.remove = function() {
    //  prototype to allow removal of element by name
    var what, a = arguments, L = a.length, ax;
    while (L && this.length) {
        what = a[--L];
        while ((ax = this.indexOf(what)) !== -1) {
            this.splice(ax, 1);
        }
    }
    return this;
};


var generateSampleList = function (data) {
    var sampleIds = data['labels']
    sampleIds.forEach(function(val, index){
        $('#sampleList').append('<li>' + val + '</li>')
    })

}

var constructToolBar =  function() {

    function changeSample() {
        var selection = this.options[this.selectedIndex].value
        console.log('changed!')
        d3.select('svg').remove()

        visualPlot(selection)

    }


    d3.select("#selectType").on("change", changeSample);


    var populateSelection =  function(selections) {
        var select = d3.select('#selectType').selectAll('option').data(selections)
        console.log(select)
        select.on("change", changeSample)
        select.enter().append("option").text(function(d) {return d })
    }
    populateSelection(Object.keys(data).remove('labels'));
}

var visualPlot = function(selections) {
        var n = 3, // number of layers //
        m = 25, // number of samples per layer
        stack = d3.layout.stack(),
        layers = stack(data[selections]['values']), //  need to change this
        yGroupMax = d3.max(layers, function (layer) {
            return d3.max(layer, function (d) {
                return d.y;
            });
        }),
        yStackMax = d3.max(layers, function (layer) {
            return d3.max(layer, function (d) {
                return d.y0 + d.y;
            });
        });

    var margin = {top: 40, right: 10, bottom: 20, left: 100},
        width = 960 - margin.left - margin.right ,
        height = 500 - margin.top - margin.bottom;

    var x = d3.scale.ordinal()
        .domain(d3.range(m))
        .rangeRoundBands([0, width], .08);

    var y = d3.scale.linear()
        .domain([0, yStackMax])
        .range([height, 0]);

    var color = d3.scale.linear()
        .domain([0, n - 1]) // domain for the colour scale
        .range(["#aad", "#556"]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .tickSize(0)
        .tickPadding(6)
        .orient("bottom");


    var yAxis = d3.svg.axis()
        .scale(y)
        .tickSize(0)
        .tickPadding(1)
        .orient("left")

    var zoom = d3.behavior.zoom()
        .scaleExtent([1, 10])
        .on("zoom", zoomed);

    var svg = d3.select("#chart").append("svg")
        .attr("width", width + margin.left + margin.right + 150)
        .attr("height", height + margin.top + margin.bottom)
        .attr("class", 'theplot')
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
        .call(zoom);;

    var layer = svg.selectAll(".layer")
        .data(layers)
        .enter().append("g")
        .attr("class", "layer")
        .style("fill", function (d, i) {
            return color(i);
        });

    var rect = layer.selectAll("rect")
        .data(function (d) {
            return d;
        })
        .enter().append("rect")
        .attr("x", function (d) {
            return x(d.x);
        })
        .attr("y", height)
        .attr("width", x.rangeBand())
        .attr("height", 0);

    rect.transition()
        .delay(function (d, i) {
            return i * 10;
        })
        .attr("y", function (d) {
            return y(d.y0 + d.y);
        })
        .attr("height", function (d) {
            return y(d.y0) - y(d.y0 + d.y);
        });

    var legendColor = d3.scale.ordinal()
        .domain(data[selections]['legend'])
        .range(["#aad", "#556"]);

    console.log(data[selections]['legend'])


    var legend = svg.selectAll(".legend")
        .data(data[selections]['legend'])
        .enter().append("g")
        .attr("class", "legend")
        .attr("transform", function (d, i) {
            return "translate(50," + 10 * i + ")";
        });

    legend.append("rect")
        .attr("x", width - 10)
        .attr("width", 10)
        .attr("height", 10)
        .style("fill", function (d, i) {
            return color(i);
        })
        .style("stroke", "grey");

    legend.append("text")
        .attr("x", width - 12)
        .attr("y", 6)
        .attr("dy", ".35em")
        .style("text-anchor", "end")
        .text(function (d) {
            return d;
        });


    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)


    svg.append("g")
        .attr("class", "y axis")
        .attr("transform", "translate(0,0)")
        .call(yAxis)


    d3.selectAll("input").on("change", change);


    var timeout = setTimeout(function () {
        d3.select("input[value=\"grouped\"]").property("checked", true).each(change);
    }, 2000);

    function change() {
        clearTimeout(timeout);
        if (this.value === "grouped") transitionGrouped();
        else transitionStacked();
    }

    function transitionGrouped() {
        y.domain([0, yGroupMax]);

        rect.transition()
            .duration(500)
            .delay(function (d, i) {
                return i * 10;
            })
            .attr("x", function (d, i, j) {
                return x(d.x) + x.rangeBand() / n * j;
            })
            .attr("width", x.rangeBand() / n)
            .transition()
            .attr("y", function (d) {
                return y(d.y);
            })
            .attr("height", function (d) {
                return height - y(d.y);
            });
    }

    function transitionStacked() {
        y.domain([0, yStackMax]);

        rect.transition()
            .duration(500)
            .delay(function (d, i) {
                return i * 10;
            })
            .attr("y", function (d) {
                return y(d.y0 + d.y);
            })
            .attr("height", function (d) {
                return y(d.y0) - y(d.y0 + d.y);
            })
            .transition()
            .attr("x", function (d) {
                return x(d.x);
            })
            .attr("width", x.rangeBand());

    }



    function zoomed() {
        svg.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
    }





}