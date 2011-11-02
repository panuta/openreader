
var calendarDialog;
var calendarWidget;
var activeCalendarInputID;

YAHOO.util.Event.onDOMReady(function(){
	initializeYUICalendar();
	
	var date_pickers = YAHOO.util.Dom.getElementsByClassName('yui_date_picker');
	
	for(var i=0; i<date_pickers.length; i++) {
		YAHOO.util.Event.on(date_pickers[i], "click", function(e) {
			e.preventDefault();
			activeCalendarInputID = e.target.id;
			triggerYUICalendar();
		});
	}
	
	// Open Date Picker calendar when click at textbox
	$(".yui_date_picker_textbox").click(function(e) {
		activeCalendarInputID = $(this).parent().find(".yui_date_picker").attr('id');
		triggerYUICalendar();
	});
});

function triggerYUICalendar() {
	var date_value = YAHOO.util.Dom.get(activeCalendarInputID + '_value').getAttribute('value');
	
	if(date_value) {
		var date_array = date_value.split('-');
		
		calendarWidget.select(date_array[1] + '/' + date_array[2] + '/' + (parseInt(date_array[0]) + 543));
		calendarWidget.cfg.setProperty("pagedate", date_array[1] + '/' + (parseInt(date_array[0]) + 543));
		calendarWidget.render();
		
	} else {
		var seldate = calendarWidget.getSelectedDates();
		
		if (seldate.length > 0) {
			calendarWidget.cfg.setProperty("pagedate", seldate[0]);
			calendarWidget.render();
		}
	}
	
	calendarDialog.cfg.setProperty('context', [activeCalendarInputID, "tl", "bl"]);
	calendarDialog.show();
}

function initializeYUICalendar() {
	var Event = YAHOO.util.Event, Dom = YAHOO.util.Dom;
	
	if(!calendarDialog) {
		/* ---------- Initialize Dialog ---------- */
		
		// Hide Calendar if we click anywhere in the document other than the calendar
		Event.on(document, "click", function(e) {
			var showBtn = Dom.get(activeCalendarInputID);
			var showTextbox = Dom.get(activeCalendarInputID+'_display');
			var el = Event.getTarget(e);
			var dialogEl = calendarDialog.element;
			if (el != dialogEl && !Dom.isAncestor(dialogEl, el) && el != showBtn && !Dom.isAncestor(showBtn, el) && el != showTextbox && !Dom.isAncestor(showTextbox, el)) {
				calendarDialog.hide();
			}
		});
		
		calendarDialog = new YAHOO.widget.Dialog("container", {
			visible:false,
			draggable:false,
			close:false
		});
		
		calendarDialog.setBody('<div id="cal"></div>');
		calendarDialog.render(document.body);
		
		calendarDialog.showEvent.subscribe(function() {
			if (YAHOO.env.ua.ie) {
				calendarDialog.fireEvent("changeContent");
			}
		});
	}
	
	if(!calendarWidget) {
		/* ---------- Initialize Calendar ---------- */
		calendarWidget = new YAHOO.widget.Calendar("cal", {
			iframe:false,
			hide_blank_weeks:false,
			year_offset:543,
			navigator:true
		});
	
		var months = ["มกราคม","กุมภาพันธ์","มีนาคม","เมษายน","พฤษภาคม","มิถุนายน","กรกฎาคม","สิงหาคม","กันยายน","ตุลาคม","พฤศจิกายน","ธันวาคม"]; 
		var weekdays = ["อา.", "จ.", "อ.", "พ.", "พฤ.", "ศ.", "ส."]; 

		calendarWidget.cfg.setProperty("MONTHS_LONG", months); 

		calendarWidget.cfg.setProperty("WEEKDAYS_1CHAR", weekdays); 
		calendarWidget.cfg.setProperty("WEEKDAYS_SHORT", weekdays); 
		calendarWidget.cfg.setProperty("WEEKDAYS_MEDIUM", weekdays); 
		calendarWidget.cfg.setProperty("WEEKDAYS_LONG", weekdays); 
		
		calendarWidget.render();
		
		calendarWidget.selectEvent.subscribe(function() {
			if (calendarWidget.getSelectedDates().length > 0) {
				
				var selDate = calendarWidget.getSelectedDates()[0];
				
				var dStr = selDate.getDate();
				var mStr = calendarWidget.cfg.getProperty("MONTHS_LONG")[selDate.getMonth()];
				var yStr = selDate.getFullYear() + 543;
				
				var old_value = Dom.get(activeCalendarInputID + '_value').value;
				var new_value = selDate.getFullYear() + '-' + (selDate.getMonth()+1) + '-' + selDate.getDate();
				var new_display_value = dStr + " " + mStr + " " + yStr;

				Dom.get(activeCalendarInputID + '_value').value = new_value;
				Dom.get(activeCalendarInputID + '_display').value = new_display_value;
				//Dom.get(activeCalendarInputID + '_display').innerHTML = new_display_value;

				if(typeof onCalendarChangeCallback == 'function') {
					onCalendarChangeCallback(activeCalendarInputID, selDate, new_value, new_display_value);
				}
				
				if(old_value != new_value) YAHOO.util.Dom.addClass(activeCalendarInputID + '_display', 'changed');
				
				calendarDialog.hide();
				
			} else {
				Dom.get(activeCalendarInputID + '_value').value = '';
				Dom.get(activeCalendarInputID + '_display').value = '';
			}
		});
	
		calendarWidget.renderEvent.subscribe(function() {
			calendarDialog.fireEvent("changeContent");
		});
	}
}