$(function() {
    var $tweet = $('.js-tweet'),
        num = 0,
        tweetsLength = $tweet.length,
        speed = 5000,

        sliderNum = 0,
        $slide = $('.js-slide'),
        slideLength = $slide.length,

        $ratingEntry = $('.js-rating-entry'),
        $ratingTabLink = $('.js-rating-tab-link'),
        currRatingTab = 'b-rating__tabs-item_state_current',

        $statisticsTabLink = $('.js-statistics-tab-link'),
        $statisticsEntry = $('.js-statistics-entry'),
        currStatisticsTab = 'b-statistics__tabs-item_state_current',

        $statisticsSubTabLink = $('.js-statistics-sub-tab-link'),
        $statisticsSubEntry = $('.js-statistics-sub-entry'),
        $statisticsSubTabs = $('.b-statistics__sub-tabs'),
        currStatisticsSubTab = 'b-statistics__sub-tabs-item_state_current';

    function getUrlVars()
    {
        var vars = [], hash;
        var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
        for(var i = 0; i < hashes.length; i++)
        {
            hash = hashes[i].split('=');
            vars.push(hash[0]);
            vars[hash[0]] = hash[1];
        }
        return vars;
    }

    document.ready = switcher;
    var status = "";
    function switcher() {

        var t = getUrlVars()["active"];
        var allOrAct = $('#allOrActiveInput');

        status = $('#filter-status');
        $('#allOrActiveInput').val('Active');
        activeOption = $('#activeOption');
       if(t == 1){

           $('#filter-status li:eq(0)').addClass('b-form__dropdown-item_state_selected');
           $('#filter-status li:eq(1)').removeClass('b-form__dropdown-item_state_selected');
           $('#allOrActiveInput').val('Active');

       } else if (t == 0) {

           $('#filter-status li:eq(1)').addClass('b-form__dropdown-item_state_selected');
           $('#filter-status li:eq(0)').removeClass('b-form__dropdown-item_state_selected');
           $('#allOrActiveInput').val('All');
       }
    }

    // Twetter feed
    function blink(direction) {
        $tweet.eq(num).animate(speed, function() {
            $tweet.hide();
            num = direction ? ((num - 1) % tweetsLength) : ((num + 1) % tweetsLength);
            $tweet.eq(num).fadeIn(500);
        });
    }

    var timer = window.setInterval(blink, speed);

    $('.js-tweets').hover(function() {
            window.clearInterval(timer)
        }, function() {
            timer = window.setInterval(blink, speed);
        }
    );

    $('.js-tweets-prev').click(function() {
        blink('prev');
    });

    $('.js-tweets-forward').click(function() {
        blink();
    });

    // Study section
    function slider(direction) {
        $slide.hide();
        sliderNum = direction ? ((sliderNum - 1) % slideLength) : ((sliderNum + 1) % slideLength);
        $slide.eq(sliderNum).show();
    }

    $('.js-slider-prev').click(function() {
        slider('prev');
        return false;
    });

    $('.js-slider-forward').click(function() {
        slider();
        return false;
    });

    // Show current rating tab
    $ratingEntry.filter('[data-num=' + $('.' + currRatingTab).data('tab') + ']').css({
        visibility: 'visible',
        height: 'auto'
    });

    $ratingTabLink.click(function() {
        var $this = $(this);

        if(!$this.parent().hasClass(currRatingTab)) {
            $ratingEntry.filter(':visible').css({
                visibility: 'hidden'
            });
            $('.' + currRatingTab).removeClass(currRatingTab);
            $this.parent().addClass(currRatingTab);

            $ratingEntry.filter('[data-num=' + $this.parent().data('tab') + ']').css({
                visibility: 'visible',
                height: 'auto'
            });
        }

        return false;
    });

    // Show current statistic tab
    $statisticsEntry.hide();
    $statisticsEntry.filter('[data-num=' + $('.' + currStatisticsTab).data('tab') + ']').show();

    $statisticsTabLink.click(function() {
        var $this = $(this),
            $subInner = $('.b-statistics__sub-inner');

        if($this.parent().data('tab') == 2) {
            $subInner.show();
            $statisticsSubTabs.show();
        } else {
            $subInner.hide();
            $statisticsSubTabs.hide();
        }

        if(!$this.parent().hasClass(currStatisticsTab)) {
            $statisticsEntry.hide();

            $('.' + currStatisticsTab).removeClass(currStatisticsTab);
            $this.parent().addClass(currStatisticsTab);

            $statisticsEntry.filter('[data-num=' + $this.parent().data('tab') + ']').show();
        }

        return false;
    });

// Show current statistic sub tab
    $statisticsSubEntry.filter('[data-num=' + $('.' + currStatisticsSubTab).data('tab') + ']').show();

    $statisticsSubTabLink.click(function() {
        var $this = $(this);

        if(!$this.parent().hasClass(currStatisticsSubTab)) {
            $statisticsSubEntry.hide();

            $('.' + currStatisticsSubTab).removeClass(currStatisticsSubTab);
            $this.parent().addClass(currStatisticsSubTab);

            $statisticsSubEntry.filter('[data-num=' + $this.parent().data('tab') + ']').show();
        }

        return false;
    });

    // Scroll
    $('.js-sub-menu-link[href*=#], .js-scroll-top[href*=#], .js-scroll-link[href*=#]').bind('click', function(e){
        var anchor = $(this),
            link = anchor.attr('href').replace(new RegExp("#",'gi'), '');

        anchor.parents('.js-statistics-tab').find('.js-statistics-tab-link').click();

        $('html, body').stop().animate({
            scrollTop: $('[data-link=' + link + ']').offset().top
        }, 1000);

        e.preventDefault();

    }).bind("mousewheel", function (e) {
            e.preventDefault();
        }
    );

    // Hide border bottom for two last articles
    $('.js-article').slice(-2).addClass('b-articles__article_type_last');

    // DropDown list
    var activeClass = 'b-form__dropdown_type_active',
        $dropDownList = $('.js-dropdown');

    $dropDownList.click(function(){
        var list = $(this),
            $listItems = list.find('.b-form__dropdown-list');

        list.toggleClass(activeClass);
        $listItems.toggle();

        $('body').click(function(e){
            if($listItems.is(':visible')) {
                list.removeClass(activeClass);
                $listItems.hide();
            }
        });

        return false;
    });

    var selectedListClass = 'b-form__dropdown-item_state_selected';
    $('.js-dropdown-item').click(function(){
        var listItem = $(this);

        listItem.closest('div').find('.js-dropdown-item').removeClass(selectedListClass);

        listItem.closest('div').find('input').val(listItem.text().trim());


            if ( listItem.text().trim()  != "Commercial Products" ){
                $('#resultFeedBox').attr('disabled',true);
                $('#statFeedBox').attr('disabled',true);
                $('#apiFeedBox').attr('disabled',true);
                $('#fantasyFeedBox').attr('disabled',true);
                $('#devFeedBox').attr('disabled',true);
                $('#designFeedBox').attr('disabled',true);
                $('#researchFeedBox').attr('disabled',true);
                //Uncheck boxes
                $("#choice1").removeClass("b-form__checkbox_state_checked");
                $("#choice2").removeClass("b-form__checkbox_state_checked");
                $("#choice3").removeClass("b-form__checkbox_state_checked");
                $("#choice4").removeClass("b-form__checkbox_state_checked");
                $("#choice5").removeClass("b-form__checkbox_state_checked");
                $("#choice6").removeClass("b-form__checkbox_state_checked");
                $("#choice7").removeClass("b-form__checkbox_state_checked");

                //Gray out text
                $("#statSpan").css('color', "gray");
                $("#apiSpan").css('color', "gray");
                $("#fantasySpan").css('color', "gray");
                $("#devSpan").css('color', "gray");
                $("#designSpan").css('color', "gray");
                $("#researchSpan").css('color', "gray");
                $("#resultSpan").css('color', "gray");



            }  else {
                $('#resultFeedBox').attr('disabled',false);
                $('#statFeedBox').attr('disabled',false);
                $('#apiFeedBox').attr('disabled',false);
                $('#fantasyFeedBox').attr('disabled',false);
                $('#devFeedBox').attr('disabled',false);
                $('#designFeedBox').attr('disabled',false);
                $('#researchFeedBox').attr('disabled',false);

                $("#statSpan").css('color', "black");
                $("#apiSpan").css('color', "black");
                $("#fantasySpan").css('color', "black");
                $("#devSpan").css('color', "black");
                $("#designSpan").css('color', "black");
                $("#researchSpan").css('color', "black");
                $("#resultSpan").css('color', "black");
            }

        if (listItem.html().trim() === "Academic Access"){
            $("#error-message").html( "Please note that FightMetric only accepts applications for Academic Access during the months of November and May. We may not respond to requests for Academic Access during other times of the year. For more information, please visit our <a href=\"/company#academic-section\">Academic Access section</a>" );
        };

        listItem.addClass(selectedListClass);

    });

    $('.js-fighter-stats').click(function() {
        var country = $('#filter-country').find('.' + selectedListClass).data('country');
        var weight = $('#filter-weight').find('.' + selectedListClass).data('weight');
        if($('#filter-status').find('.' + selectedListClass).data('status') != null){
        var status = $('#filter-status').find('.' + selectedListClass).data('status');
        }else {
            var status = 0;
        }

        var url = '/fighter-stats';

        var delimiter = '?';

        if (country.length > 0) {
            url += delimiter + 'country=' + country;
            delimiter = '&';
        }

        if (weight.length > 0) {
            url += delimiter + 'weight=' + weight;
            delimiter = '&';
        }

        url += delimiter + 'active=' + status;

        console.log(url);
        window.location = url;
    });

    $('.js-rankings').click(function() {
        window.location.hash = $(this).data('anchor');
    });

    $.each($dropDownList, function() {
        $(this).find('.b-form__field').val($(this).find('.' + selectedListClass).text().trim());
    });


    /* Show alt */
    $('.js-alt')
        .mouseover(function() {
            $(this).find('.b-rating__alt').show();
        })
        .mouseout(function() {
            $(this).find('.b-rating__alt').hide();
        });

    /* Fantasy page tabs */
    var $fantasyTab = $('.js-tab'),
        currentClass = 'b-fantasy__tab_state_current';

    /* Image slider */
    var $imagesBlock = $('.js-image-slider'),
        $image = $imagesBlock.find('.b-fantasy__image');

    $.each($('.' + currentClass), function() {
        $(this).closest($imagesBlock).find($image).eq($('.' + currentClass).index()).show();
    });

    $fantasyTab.click(function() {
        var $this = $(this);

        if(!$this.hasClass(currentClass)) {
            $this.closest($imagesBlock).find($image).filter(':visible').hide();
            $this.closest($imagesBlock).find($image).eq($this.index()).fadeIn(300);

            $this.closest($imagesBlock).find($('.' + currentClass)).removeClass(currentClass);
            $this.addClass(currentClass);
        }
    });

    /* Checkbox */
    var $checkBox = $('.js-checkbox'),
        checkedCheckboxClass = 'b-form__checkbox_state_checked';

    $checkBox.click(function() {
        if($(this).find('.b-form__checkbox-field:checked').length != 0) {
            $(this).find('i').addClass(checkedCheckboxClass);
        } else {
            $(this).find('i').removeClass(checkedCheckboxClass);
        }
    });


    /* Contact us form */
    var $form = $('.b-form'),
        $fieldInner = $('.b-form__field-inner'),
        $field = $('.b-form__field'),
        $submit = $('.js-submit'),
        $messageBox = $('.b-form__field_type_message'),
        $submitBtn = $('.b-form__submit-inner'),
        $closeBoxBtn = $('.js-message-close'),
        data = {};

    $submit.click(function(){
        if (!$('form').valid()) {
            return false;
        }
        data = $form.serialize();

        $.ajax({
           type: 'POST',
           url: 'contact-us',
           beforeSend: function(){
            $('.b-form__message').remove();
           },
           data: data,
           cache: false,
           success: function(data) {
               /*$submitBtn.after('<div class="b-form__message b-form__message_type_error"><a href="#" class="b-form__message-close js-message-close">×</a>' + data + '</div>');*/
               $submitBtn.after('<div class="b-form__message b-form__message_type_success"><a href="#" class="b-form__message-close js-message-close">×</a>' + data + '</div>');
           }


        });
        //clearform();
        //alert($('#contactForm input').innerHTML)

        $('#contactForm')[0].reset();
        return false;
    });

    $closeBoxBtn.click(function(){
        $('.b-form__message').hide();
        return false;
    });

    /* Fight Section */
    var $fightSection = $('.js-fight-section'),
        $fightCollapseLink = $('.js-fight-collapse-link'),
        $fightTable = $('.js-fight-table'),
        fightCurrLinkClass = 'b-fight-details__collapse-link_state_expanded';

    $fightCollapseLink.on('click', function() {
        var $this = $(this);

        if(!$this.hasClass(fightCurrLinkClass)) {
            $this.addClass(fightCurrLinkClass);
            $this.closest($fightSection).find($fightTable).show();
        } else {
            $this.removeClass(fightCurrLinkClass);
            $this.closest($fightSection).find($fightTable).hide();
        }

        return false;
    });

    $('.js-chart-name').click(function() {
        var $this = $(this);
        var color = $this.data('color');
        var $red = $('.js-red');
        var $blue = $('.js-blue'),
            activeColorClass = 'active-color';

        if($this.hasClass(activeColorClass)) {
            $red.css('opacity', 1);
            $blue.css('opacity', 1);

            $this.removeClass(activeColorClass);
        } else {
            if(color == 'red') {
                $red.css('opacity', 1);
                $blue.animate({opacity: .5}, 100);
            } else {
                $blue.css('opacity', 1);
                $red.animate({opacity: .5}, 100);
            }
            $('.js-chart-name').removeClass(activeColorClass);
            $this.addClass(activeColorClass);
        }
    });

    /* Box sizing */
    var box = 0,
        $guide = $('.js-guide');

    $guide.hide();


    $.each($guide, function() {
        var height = $(this).height();
        if (height > box) {
            box = height;
        }
    });

    $guide
        .css('height', box)
        .fadeIn(50);


    $('form').validate();

    $('.js-fight-details-click').click(function(e) {
        if (e.target == this) {
            location.href = $(this).data('link');
        }
    });
    
    // Dev bar fill resize
    
    $('#dev-bar-fill').css('width', ($(window).width() - 950)/2);
    $(window).resize(function() {
      $('#dev-bar-fill').css('width', ($(window).width() - 950)/2);
    });
});