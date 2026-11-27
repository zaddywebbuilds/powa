<?php
/**
 * Knack Extra theme bootstrap.
 *
 * The commercial content of this site is NOT stored in WordPress. It is read
 * from assets/js/config.js, exactly as it is on the static build, so that a
 * price or a policy has one home. See README-WORDPRESS.md.
 *
 * @package knack-extra
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'KNACK_VERSION', '1.0.0' );

require_once get_theme_file_path( 'inc/assets.php' );
require_once get_theme_file_path( 'inc/order-form.php' );
require_once get_theme_file_path( 'inc/customizer.php' );
require_once get_theme_file_path( 'inc/seo.php' );

/**
 * Theme supports.
 */
function knack_setup() {
	add_theme_support( 'title-tag' );
	add_theme_support( 'responsive-embeds' );
	add_theme_support(
		'html5',
		array( 'search-form', 'comment-form', 'comment-list', 'gallery', 'caption', 'style', 'script' )
	);
}
add_action( 'after_setup_theme', 'knack_setup' );

/**
 * The emoji script is dead weight on a one page sales site.
 */
function knack_trim_head() {
	remove_action( 'wp_head', 'print_emoji_detection_script', 7 );
	remove_action( 'wp_print_styles', 'print_emoji_styles' );
	remove_action( 'wp_head', 'wp_generator' );
	remove_action( 'wp_head', 'wlwmanifest_link' );
	remove_action( 'wp_head', 'rsd_link' );
}
add_action( 'init', 'knack_trim_head' );
