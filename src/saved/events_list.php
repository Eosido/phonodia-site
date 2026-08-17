<?php 
/*
	@var 
		$events_to_show = array(
			array(
				'thumbnail'
				'dateObj'	=>	DateTime()
				'event_date_computed'
				'event_time'
				'event_location'
				'event_venue'
				'event_buy_tickets_message'
				'event_buy_tickets_url'
				'event_url',
				'multiday'	=> true/false
				'endDateObj'	=> DateTime()
				'event_end_date_computed'
				'event_sold_out'	=> true/false
				'event_canceled'	=> true/false
			)
		);
		$show_event_year	
*/
?>

<ul class="events_list">
	<?php


	foreach ($events_to_show as $event) {
	?>
		<li class="single_event_list clearfix">
			<a href="<?php echo esc_url($event['event_url']); ?>">
				<div class="event_list_entry event_date">
					<?php
					$el_day = $event['dateObj']->format('d');
					$el_month = $event['dateObj']->format('M');
					$el_year = $event['dateObj']->format('Y');
					$el_month = SLIDE_SWP_get_translated_month($el_month);

					$dateObjectNow = new DateTime('NOW');
					$schema_time = $dateObjectNow->format(DateTime::ATOM);
					$output_time = '';	
					if ($event['event_time'] != '') {
						$build_time = "20000101"." ".$event['event_time'].":00";
						if (strtotime($build_time)) {
							$time_obj =  new DateTime($build_time);
							$output_time = $time_obj->format(get_option('time_format'));
							$schema_time = $time_obj->format(DateTime::ATOM);
						} else {
							$output_time = $event['event_time'];
						}		
					}
					
					$dateObjectTomorrow = new DateTime('tomorrow');
					$is_event_today = ($dateObjectNow->format('Y-m-d') == $event['dateObj']->format('Y-m-d')) ? true : false;
					$is_event_tomorrow = ($dateObjectTomorrow->format('Y-m-d') == $event['dateObj']->format('Y-m-d')) ? true : false;

					$have_multiday_date = false;
					if ($event['multiday']) {
						if ($event['endDateObj'] != "") {
							$el_end_day = $event['endDateObj']->format('d');
							$have_multiday_date = true;
						}
					}					

					?>
					<div class="text_center event_list_date_container">
						<div class="eventlist_day">
							<?php 
							echo esc_html($el_day);
							if ($have_multiday_date) {
								echo esc_html("-") . $el_end_day;
							}
							?>
						</div>
						<div class="eventlist_month"><?php echo esc_html($el_month); ?></div>
						<?php if ($show_event_year) { ?>
						<div class="eventlist_year"><?php echo esc_html($el_year); ?></div>
						<?php } ?>
					</div>
				</div>

				<div class="event_list_entry event_title_img clearfix">
					<?php if (strlen($event['thumbnail'])) { ?>
						<div class="event_img"> 
							<img src="<?php echo esc_url($event['thumbnail']); ?>" alt="<?php echo esc_attr($event['event_title']); ?>">
						</div>
					<?php } ?>
					<div class="evnt_list_title_loc">
						<div class="event_list_title"><?php echo esc_html($event['event_title']); ?></div>
						<div class="event_list_location"> <?php echo esc_html($event['event_location']); ?> </div>
					</div>
				</div>

				<div class="event_list_entry event_venue">
					<i class="fas fa-map-marker-alt" aria-hidden="true"></i>
					<?php echo esc_html($event['event_venue']); ?>
				</div>


				<div class="event_list_entry event_time">
					<?php if ($is_event_today) { ?>
					<span class="et_today"><?php echo esc_html__("Today", 'slide'); ?></span>
					<?php } ?>
					<?php if ($is_event_tomorrow) { ?>
					<span class="et_today"><?php echo esc_html__("Tomorrow", 'slide'); ?></span>
					<?php } ?>
					<i class="far fa-clock" aria-hidden="true"></i>
					<?php echo esc_html($output_time); ?>
				</div>

				<div class="event_list_entry event_buy">
						<?php
						$button_class = "event_buy_btn ";
						$button_text = "";
						$event_ticket_url = $event['event_buy_tickets_url'];
						$ticket_click_target = $event['event_buy_tickets_target'];
						$show_arrow = false;


						if ($event['event_canceled']) {
							$button_class .= "event_canceled";
							$button_text = esc_html__("Canceled", 'slide');
						} elseif ($event['event_sold_out']) {
							$button_class .= "event_sold_out";
							$button_text = esc_html__("Sold Out", 'slide');
						} else {
							if (empty($ticket_click_target)) {
								$ticket_click_target = "_blank";
							}

							if (empty($event['event_buy_tickets_url'])) {
								$event_ticket_url = $event['event_url'];
								$ticket_click_target = "_self";
							}

							$button_class .= "lc_js_link";
							$button_text = $event['event_buy_tickets_message'];
						}
						?>

						<?php if (!empty($event['event_buy_tickets_message'])) { ?>
							<div class="<?php echo esc_attr($button_class); ?>" data-href="<?php echo esc_url($event_ticket_url); ?>" data-target="<?php echo esc_attr($ticket_click_target); ?>">

								<?php echo esc_html($button_text); ?>
								<?php if ($show_arrow) { ?>
								<i class="fas fa-arrow-right" aria-hidden="true"></i>
								<?php } ?>
							</div>
						<?php } ?>
				</div>
			</a>
		</li>
	<?php 
	} 
	?>
</ul>