<?php
/**
 * Customizer settings.
 *
 * Only genuinely WordPress-side settings belong here. Prices, policies and
 * contact details stay in assets/js/config.js so that there is one place to
 * change them and one place to audit them.
 *
 * @package knack-extra
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Register the order form setting.
 *
 * @param WP_Customize_Manager $wp_customize Customizer instance.
 */
function knack_customize_register( $wp_customize ) {
	$wp_customize->add_section(
		'knack_order',
		array(
			'title'       => __( 'Knack Extra order form', 'knack-extra' ),
			'priority'    => 30,
			'description' => __( 'The Fluent Forms form rendered in the "Place your order" section. Find the ID under Fluent Forms, All Forms.', 'knack-extra' ),
		)
	);

	$wp_customize->add_setting(
		'knack_form_id',
		array(
			'default'           => 42,
			'sanitize_callback' => 'absint',
			'transport'         => 'refresh',
		)
	);

	$wp_customize->add_control(
		'knack_form_id',
		array(
			'label'       => __( 'Fluent Forms form ID', 'knack-extra' ),
			'section'     => 'knack_order',
			'type'        => 'number',
			'input_attrs' => array( 'min' => 0, 'step' => 1 ),
		)
	);
}
add_action( 'customize_register', 'knack_customize_register' );
