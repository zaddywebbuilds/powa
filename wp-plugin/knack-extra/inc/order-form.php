<?php
/**
 * The order form.
 *
 * The form itself is a Fluent Forms form, so every order is recorded as an
 * entry in WordPress and the fields can be changed without touching code.
 * This file only decides where it sits and what it looks like.
 *
 * @package knack-extra
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * The configured form ID.
 *
 * @return int
 */
function ke_form_id() {
	return absint( apply_filters( 'knack_form_id', absint( get_option( 'knack_form_id', 42 ) ) ) );
}

/**
 * Is Fluent Forms available to render a form?
 *
 * @return bool
 */
function ke_forms_active() {
	return shortcode_exists( 'fluentform' );
}

/**
 * Does the current request show the order form?
 *
 * @return bool
 */
function ke_has_order_form() {
	return KNACK_TPL_SALES === ke_current_template();
}

/**
 * Render the order form, or an honest fallback.
 *
 * A half-working form is worse than none: if Fluent Forms is not active, or
 * no form ID is set, the section says so and points at the support channel
 * rather than printing an empty box or a raw shortcode.
 */
function ke_order_form() {
	$id = ke_form_id();

	if ( $id > 0 && ke_forms_active() ) {
		echo '<div class="ke-form" data-ke-form="' . esc_attr( $id ) . '">';
		echo do_shortcode( '[fluentform id="' . $id . '"]' );
		echo '</div>';
		return;
	}

	echo '<div class="ke-form ke-form-missing">';
	echo '<p class="lede">The order form is not available at the moment. Please message us and we will take your order directly.</p>';
	echo '<p><a href="#" class="btn btn-lg" data-support-link>Message support</a></p>';
	echo '</div>';
}

/**
 * Tell the administrator, not the customer, when the form cannot render.
 */
function ke_order_form_notice() {
	if ( ! current_user_can( 'manage_options' ) ) {
		return;
	}

	if ( ! ke_forms_active() ) {
		echo '<div class="notice notice-error"><p><strong>Knack Extra:</strong> Fluent Forms is not active, so the order form cannot render. Customers are being shown the support link instead.</p></div>';
		return;
	}

	if ( ke_form_id() < 1 ) {
		echo '<div class="notice notice-warning"><p><strong>Knack Extra:</strong> no order form is selected. Choose one under Settings, Knack Extra.</p></div>';
	}
}
add_action( 'admin_notices', 'ke_order_form_notice' );
