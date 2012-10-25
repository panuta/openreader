$(document).ready( function () {
  $(window).bind('hashchange', hashCheck);
  hashCheck();

	hide_all_after_click();
  //Add active class on Intruduction menu
  $(".nav-item-1").addClass("active");
  //Find position of each menu
  var position_feature = $("#features").position();
  var position_price = $("#price-plan").position();
  var position_contact = $("#contact-us").position();
  //Check scroll position
  $(window).scroll(function(){
    //$("#position").text($(window).scrollTop());
    if ($(window).scrollTop() >= 330) {
      $("#header").addClass("small-header");
    } else {
      $("#header").addClass("header");
      $("#header").removeClass("small-header");
    }

    if (position_feature){
      if ($(window).scrollTop() >= 0 && $(window).scrollTop() < position_feature.top) {
        remove_class_active_nav();
        $(".nav-item-1").addClass("active");
      } else if ($(window).scrollTop() >= position_feature.top && $(window).scrollTop() < position_price.top-50) {
        remove_class_active_nav();
        $(".nav-item-2").addClass("active");
      } else if ($(window).scrollTop() >= position_price.top-50 && $(window).scrollTop() < position_price.top+150) {
        remove_class_active_nav();
        $(".nav-item-3").addClass("active");
      } else if ($(window).scrollTop() >= position_price.top+150) {
        remove_class_active_nav();
        $(".nav-item-4").addClass("active");
      } else {
        remove_class_active_nav();
      }
    }
  });

  /** Show & Hide effect **/
  $(".showr").click(function (event) {
    $(".showr").removeClass("active");
    event.preventDefault();
  	class_name = $(this).attr("class");
  	var class_name_part = class_name.split("-");
  	if (class_name_part[1]) {
  		var after_click_class_name = "feature-"+class_name_part[1];
      var dp = $(".feature-"+class_name_part[1]).css("display");
      if (dp != 'block') {
        $(this).addClass("active");
        show_only_after_click(after_click_class_name);
      }
  	}
  });

  $(".hidr").click(function (event) {
    event.preventDefault();
    class_name = $(this).attr("class");
    var class_name_part = class_name.split("-");
    var class_name_part2 = class_name_part[1].split(" ");
    if (class_name_part2[0]) {
      hide_with_effect();
    }
  });

});

function hide_only_after_click(show_class) {
  hide_all_after_click();
  $("."+show_class).slideDown(800);
}

function show_only_after_click(show_class) {
	hide_all_after_click();
  $("."+show_class).slideDown(800);
  $('html, body').animate({ scrollTop: $("."+show_class).offset().top - 430 }, 500);
}

function hide_with_effect() {
  $(".after-click").slideUp(800);
}

function hide_all_after_click() {
	$(".after-click").hide();
}
//Remove all active class on Header Menu.
function remove_class_active_nav() {
  $("#nav li a").removeClass("active");
}

/**
 * Remove & add active class on Header Menu.
 */
function hashCheck() {
  var hash = location.hash;
  $("#nav li a").removeClass("active");
  $("#nav li a[href$='" + hash  + "']").addClass("active");
}