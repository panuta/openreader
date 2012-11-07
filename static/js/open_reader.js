$(document).ready(function() {
    var $html = $('html');
    var $window = $(window);
    var $header = $('#header');
    var $features = $('#features');
    var $price = $('#price-plan');
    var $contact = $('#contact-us');
    var $navItems = $('#nav li a');
    var $featureList = $('.feature-desc-list');
    var $featureDesc = $('.feature');
    var $featureItems = $('.feature-icon a');
    var $featureClose = $('a.hidr');
    var $question = $('.question');
    var $answer = $('.answer');
    var heightList = {};

    $featureDesc.each(function() {
        var dataId = $(this).attr('id');
        var id = parseInt(dataId.split('-')[2]);
        heightList[id] = $(this).height();
    });

    var getHeight = function(index) {
        return heightList[index] || 0;
    };

    var $scrollElement = (function() {
        var $html = $(document.documentElement),
            $body = $(document.body),
            bodyScrollTop;
        if ($html.scrollTop()) {
            return $html;
        }
        else {
            bodyScrollTop = $body.scrollTop();
            if ($body.scrollTop(bodyScrollTop + 1).scrollTop() == bodyScrollTop) {
                return $html;
            } else {
                // We actually scrolled, so undo it
                return $body.scrollTop(bodyScrollTop);
            }
        }
    }());

    var setActiveNav = function(index) {
        $navItems.removeClass('active');
        $('.nav-item-' + index).addClass('active');
    };

    var onHashChange = function() {
        var hash = location.hash;
        $navItems.removeClass("active");
        $('a[href=' + hash  + ']').addClass("active");
    };

    var showFeatureDesc = function(feature, id) {
        var scrollTop = 0;
        if (id <= 3) {
            scrollTop = $featureList.offset().top - 430;
        }
        else {
            scrollTop = $featureList.offset().top - 150;
            feature.css('top', -360);
        }
        $scrollElement.animate({ 'scrollTop': scrollTop }, 500);

        $featureDesc.hide();
        feature.show();

        feature.animate({ 'top': 0 });
        $featureList.animate({ 'height': getHeight(id) });

        // Set selected.
        selectedFeature = id;
    };

    var closeFeatureDesc = function(feature, id, newFeature, newId) {
        var scrollTop = 0;
        if (id > 3) {
            scrollTop = feature.offset().top - 430;
            $scrollElement.animate({ 'scrollTop': scrollTop }, 500);
        }

        $featureList.animate({ 'height': 0 }, 500, function() {
            selectedFeature = 0;
            $('.feature-item-' + id + ' a').removeClass('active');
            if (typeof newFeature !== 'undefined' && id !== newId) {
                showFeatureDesc(newFeature, newId);
            }
        });
    };

    if (window.front) {
        $window.scroll(function() {
            var featuresTop = $features.position().top;
            var priceTop = $price.position().top - 50;
            var contactTop = $contact.position().top;
            var winTop = $window.scrollTop();

            // Active navigation.
            if (winTop < featuresTop) {
                setActiveNav(1);
            }
            else if (winTop < priceTop) {
                setActiveNav(2);
            }
            else if (winTop < contactTop) {
                setActiveNav(3);
            }
            else {
                setActiveNav(4);
            }

            // Change header when scroll down .
            if ($window.scrollTop() >= 330) {
                $header.addClass("small-header");
            } else {
                $header.addClass("header");
                $header.removeClass("small-header");
            }
        });
    }

    // Features effect.
    var selectedFeature = 0;
    $featureItems.click(function(e) {
        var that = $(this);
        var dataId = that.attr('data-id');
        var id = parseInt(dataId.split('-')[2]);
        var $feature = $('#'+ dataId);
        var $selectedFeature = null;

        // Set active.
        $featureItems.removeClass('active'); 
        that.addClass('active');

        if (selectedFeature > 0) {
            $selectedFeature = $('#feature-desc-' + selectedFeature);
            closeFeatureDesc($selectedFeature, selectedFeature, $feature, id);
        }
        else {
            showFeatureDesc($feature, id);
        }

        e.preventDefault();
    });
    
    $featureItems.mouseenter(function(e) {
        if (selectedFeature > 0) return;

        var that = $(this);
        var dataId = that.attr('data-id');
        var id = parseInt(dataId.split('-')[2]);
        var $feature = $('#'+ dataId);

        $featureDesc.hide();
        $feature.show();
        if (id <= 3) {
            
        }
        else {
            $feature.css('top', -360);
        }
        $featureList.stop().animate({ 'height': 40 }, { 'queue': false, 'duration': 300, 'complete': function() {
            // $featureList.css('overflow', 'visible');
        }});
    });
    
    $featureItems.mouseleave(function(e) {
        if (selectedFeature > 0) return;

        var that = $(this);
        var dataId = that.attr('data-id');
        var id = parseInt(dataId.split('-')[2]);
        var $feature = $('#'+ dataId);

        $featureList.stop().animate({ 'height': 0 }, { 'queue': false, 'duration': 300, 'complete': function() {
            $feature.css('top', 0);
            // $featureList.css('overflow', 'visible');
        }});
    });

    // Hide description.
    $featureClose.click(function(e) {
        var that = $(this);
        var dataId = that.attr('data-id');
        var id = parseInt(dataId.split('-')[2]);
        var $feature = $('#'+ dataId);

        closeFeatureDesc($feature, id);

        e.preventDefault();
    });
    
    // Hide all description.
    $featureList.css('height', 0);
    $featureDesc.hide();

    // Handle hash.
    $window.bind('hashchange', onHashChange);
    $window.trigger('hashchange');

    // FAQ
    var selectedQuestion = 0;
    $question.click(function(e) {
        if (selectedQuestion > 0) {
            $answer.each(function() {
                $(this).slideUp();
            });
        }

        var answer = $(this).siblings('.answer');
        if (answer.is(':visible')) {
            answer.slideUp();
            selectedQuestion = 0;
        }
        else {
            answer.slideDown();
            selectedQuestion = $(this).attr('data-id');
        }

        e.preventDefault();
    });

    // Hide FAQ answer.
    $answer.hide();
});
