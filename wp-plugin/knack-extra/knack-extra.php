<?php
/**
 * Plugin Name:       Knack Extra sales page
 * Description:       Renders the Knack Extra sales page and its policies page on any two pages you choose, without touching the active theme or any other page on the site. Prices and policies are read from assets/js/config.js.
 * Version:           1.0.0
 * Requires at least: 6.0
 * Requires PHP:      7.4
 * Author:            Zaddy Web Builds
 * License:           GPL-2.0-or-later
 * Text Domain:       knack-extra
 *
 * WHY A PLUGIN AND NOT A THEME
 * ----------------------------
 * This site carries several sales pages. A theme governs every page on the
 * site, so shipping this as a theme would have restyled all of them and taken
 * over the home page. A plugin leaves the active theme exactly where it is and
 * claims only the pages you assign its template to.
 *
 * @package knack-extra
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'KNACK_VERSION', '1.0.0' );
define( 'KNACK_FILE', __FILE__ );
define( 'KNACK_DIR', plugin_dir_path( __FILE__ ) );
define( 'KNACK_URL', plugin_dir_url( __FILE__ ) );

/** The page template slugs this plugin registers. */
const KNACK_TPL_SALES    = 'knack-extra-sales';
const KNACK_TPL_POLICIES = 'knack-extra-policies';

require_once KNACK_DIR . 'inc/template.php';
require_once KNACK_DIR . 'inc/assets.php';
require_once KNACK_DIR . 'inc/order-form.php';
require_once KNACK_DIR . 'inc/settings.php';
require_once KNACK_DIR . 'inc/seo.php';
