<?php
/**
 * Settings, Knack Extra.
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
 * Add the settings page.
 */
function ke_settings_menu() {
	add_options_page(
		__( 'Knack Extra', 'knack-extra' ),
		__( 'Knack Extra', 'knack-extra' ),
		'manage_options',
		'knack-extra',
		'ke_settings_page'
	);
}
add_action( 'admin_menu', 'ke_settings_menu' );

/**
 * Register the one setting.
 */
function ke_settings_register() {
	register_setting(
		'knack_extra',
		'knack_form_id',
		array(
			'type'              => 'integer',
			'sanitize_callback' => 'absint',
			'default'           => 42,
		)
	);
}
add_action( 'admin_init', 'ke_settings_register' );

/**
 * Render the settings page.
 */
function ke_settings_page() {
	if ( ! current_user_can( 'manage_options' ) ) {
		return;
	}

	$policies = ke_policies_url();
	?>
	<div class="wrap">
		<h1><?php esc_html_e( 'Knack Extra', 'knack-extra' ); ?></h1>

		<form action="options.php" method="post">
			<?php settings_fields( 'knack_extra' ); ?>
			<table class="form-table" role="presentation">
				<tr>
					<th scope="row">
						<label for="knack_form_id"><?php esc_html_e( 'Fluent Forms form ID', 'knack-extra' ); ?></label>
					</th>
					<td>
						<input name="knack_form_id" id="knack_form_id" type="number" min="0" step="1"
							value="<?php echo esc_attr( get_option( 'knack_form_id', 42 ) ); ?>" class="small-text">
						<p class="description">
							<?php esc_html_e( 'The form rendered in the "Place your order" section. Find the ID under Fluent Forms, All Forms.', 'knack-extra' ); ?>
						</p>
					</td>
				</tr>
			</table>
			<?php submit_button(); ?>
		</form>

		<h2><?php esc_html_e( 'Setup', 'knack-extra' ); ?></h2>
		<p>
			<?php esc_html_e( 'This plugin claims only the pages you assign its templates to. Create a page, then pick its template under Page Attributes.', 'knack-extra' ); ?>
		</p>
		<ul class="ul-disc">
			<li><strong><?php esc_html_e( 'Knack Extra sales page', 'knack-extra' ); ?></strong></li>
			<li>
				<strong><?php esc_html_e( 'Knack Extra policies', 'knack-extra' ); ?></strong>
				<?php if ( $policies ) : ?>
					&mdash; <a href="<?php echo esc_url( $policies ); ?>"><?php echo esc_html( $policies ); ?></a>
				<?php else : ?>
					&mdash; <em><?php esc_html_e( 'no page is using this template yet, so the policy links are hidden.', 'knack-extra' ); ?></em>
				<?php endif; ?>
			</li>
		</ul>
		<p>
			<?php esc_html_e( 'Fluent Forms status:', 'knack-extra' ); ?>
			<strong><?php echo ke_forms_active() ? esc_html__( 'active', 'knack-extra' ) : esc_html__( 'not active', 'knack-extra' ); ?></strong>
		</p>
	</div>
	<?php
}
