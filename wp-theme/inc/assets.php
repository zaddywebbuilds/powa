<?php
/**
 * Asset paths and enqueueing.
 *
 * @package knack-extra
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * URL of a file inside the theme's assets folder.
 *
 * The templates are generated from the static build, where every path is
 * relative ("assets/img/hero-dark.webp"). This turns one of those into a
 * theme URL, so the same markup serves both builds.
 *
 * @param string $path Path below assets/, with no leading slash.
 * @return string
 */
function ke_asset( $path ) {
	return get_theme_file_uri( 'assets/' . ltrim( $path, '/' ) );
}

/**
 * Permalink of the policies page, falling back to a sensible guess so that
 * the footer links never go nowhere.
 *
 * @return string
 */
function ke_policies_url() {
	$page = get_page_by_path( 'policies' );
	if ( $page instanceof WP_Post ) {
		return get_permalink( $page );
	}
	return home_url( '/policies/' );
}

/**
 * Paths handed to the front end. site.js falls back to relative paths when
 * this is absent, which is what happens on the static build.
 *
 * @return array
 */
function ke_paths() {
	return array(
		'assets'   => trailingslashit( get_theme_file_uri( 'assets' ) ),
		'policies' => ke_policies_url(),
		'home'     => home_url( '/' ),
	);
}

/**
 * Styles and scripts.
 *
 * The @font-face rules are inlined at the top of site.css, so there is no
 * separate font stylesheet to enqueue and no @import round trip.
 */
function knack_enqueue() {
	wp_enqueue_style(
		'knack-site',
		ke_asset( 'css/site.css' ),
		array(),
		KNACK_VERSION
	);

	wp_enqueue_style(
		'knack-theme',
		ke_asset( 'css/theme.css' ),
		array( 'knack-site' ),
		KNACK_VERSION
	);

	if ( ke_has_order_form() ) {
		wp_enqueue_style(
			'knack-fluentform',
			ke_asset( 'css/fluentform.css' ),
			array( 'knack-site' ),
			KNACK_VERSION
		);
	}

	wp_enqueue_script(
		'knack-config',
		ke_asset( 'js/config.js' ),
		array(),
		KNACK_VERSION,
		false
	);

	wp_add_inline_script(
		'knack-config',
		'window.KNACK_PATHS = ' . wp_json_encode( ke_paths() ) . ';',
		'before'
	);

	wp_enqueue_script(
		'knack-site',
		ke_asset( 'js/site.js' ),
		array( 'knack-config' ),
		KNACK_VERSION,
		true
	);

	if ( is_page_template( 'page-policies.php' ) || is_page( 'policies' ) ) {
		wp_enqueue_script(
			'knack-policies',
			ke_asset( 'js/policies.js' ),
			array( 'knack-config' ),
			KNACK_VERSION,
			true
		);
	}
}
add_action( 'wp_enqueue_scripts', 'knack_enqueue' );

/**
 * Preload the two fonts and the hero poster, as the static build does.
 */
function knack_preload() {
	$items = array(
		array( 'font', 'fonts/manrope-400.woff2' ),
		array( 'font', 'fonts/playfair-500.woff2' ),
	);
	foreach ( $items as $item ) {
		printf(
			'<link rel="preload" as="font" type="font/woff2" href="%s" crossorigin>' . "\n",
			esc_url( ke_asset( $item[1] ) )
		);
	}
	if ( is_front_page() ) {
		printf(
			'<link rel="preload" as="image" href="%s" fetchpriority="high">' . "\n",
			esc_url( ke_asset( 'img/hero-sprout-poster.webp' ) )
		);
	}
}
add_action( 'wp_head', 'knack_preload', 2 );
