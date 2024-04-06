const monitorBtn = document.getElementById('monitorBtn');
let snifferActive = false; // Flag to track sniffer state
let intervalId; // Variable to store the interval ID

monitorBtn.addEventListener('click', () => {
    $.ajax({
        type: 'POST',
        url: '/start_stop_sniffer',
        success: function() {
            // Toggle the text content and button color based on the response
            if ($('#monitorBtn').text() === 'Start Monitor') {
                $('#monitorBtn').text('Stop Monitor');
                $('#monitorBtn').removeClass('btn-success').addClass('btn-danger');
                // Start sniffer, enable fetching hosts and applications
                snifferActive = true;
                // Start fetching hosts immediately and then every second
                fetchHosts();
                fetchApplications(); // New function call
                intervalId = setInterval(function() {
                    fetchHosts();
                    fetchApplications(); // New function call
                }, 1000);
            } else {
                $('#monitorBtn').text('Start Monitor');
                $('#monitorBtn').removeClass('btn-danger').addClass('btn-success');
                // Stop sniffer, disable fetching hosts and applications
                snifferActive = false;
                clearInterval(intervalId); // Stop fetching hosts and applications
            }
        }
    });
});

// Function to fetch hosts
function fetchHosts() {
    // Check if sniffer is active
    if (!snifferActive) return;

    $.ajax({
        type: 'GET',
        url: '/send_hosts_dict',
        success: function(response) {
            var checkboxStates = storeCheckboxStates();
            var existingHosts = {};

            updateHostList(response, checkboxStates, existingHosts);

        },
        error: function(xhr, status, error) {
            console.error("Error fetching hosts:", error);
        }
    });
}


// Function to store checkbox states
function storeCheckboxStates() {
    var checkboxStates = {};
    $('.hostCheckbox').each(function() {
        var macAddress = $(this).data('mac');
        checkboxStates[macAddress] = $(this).prop('checked');
    });
    return checkboxStates;
}

// Functie om de Grab-knop toe te voegen
function addGrabButton(listItem, hostId, macAddress, ipAddress) {
    var grabButton = $('<button class="grabButton">Grab</button>').appendTo(listItem);
    grabButton.click(function() {
        grabHost(hostId, macAddress, ipAddress);
    });
}

// Functie om de Kill-knop toe te voegen
function addKillButton(listItem, hostId, macAddress, ipAddress) {
    var killButton = $('<button class="killButton">Kill</button>').appendTo(listItem);
    killButton.click(function() {
        killHost(hostId, macAddress, ipAddress);
    });
}

// Functie om de hostlijst bij te werken
function updateHostList(response, checkboxStates, existingHosts) {
    $.each(response, function(key, value) {
        var listItem = $('#hostList li[data-key="' + key + '"]');
        if (listItem.length === 0) {
            listItem = createNewListItem(key, value);
        }

        updateListItemContent(listItem, value);
        updateCheckbox(listItem, value.mac_address, checkboxStates);
        addGrabButton(listItem, key, value.mac_address, value.ip_address);
        addKillButton(listItem, key, value.mac_address, value.ip_address);

        existingHosts[value.mac_address] = true;
    });

    removeDeletedHosts(response);
}


// Function to create new list item
function createNewListItem(key, value) {
    var listItem = $('<li data-key="' + key + '"></li>').appendTo('#hostList');
    listItem.click(function(event) {
        if (!$(event.target).is(':checkbox')) {
            window.open('/host_details?id=' + key, '_blank');
        }
    });
    return listItem;
}

// Function to update list item content
function updateListItemContent(listItem, value) {
    listItem.empty();
    listItem.append('<b>Hostname:</b> ' + value.hostname + '<br>');
    listItem.append('<b>IP Address:</b> ' + value.ip_address + '<br>');
    listItem.append('<b>MAC Address:</b> ' + value.mac_address + '<br>');
    listItem.append('<b>Vendor:</b> ' + value.vendor + '<br>');
}

// Function to update checkbox
function updateCheckbox(listItem, macAddress, checkboxStates) {
    var checkbox = $('<input type="checkbox" class="hostCheckbox" data-mac="' + macAddress + '">').appendTo(listItem);
    checkbox.prop('checked', checkboxStates[macAddress]);
    checkbox.on('change', function() {
        updateCheckboxState($(this));
    });
}

// Function to update checkbox state
function updateCheckboxState(checkbox) {
    var isChecked = checkbox.prop('checked');
    var macAddress = checkbox.data('mac');
    var requestData = {
        mac_address: macAddress,
        do_not_display: isChecked
    };
    $.ajax({
        type: 'POST',
        url: '/activate_host',
        data: JSON.stringify(requestData),
        contentType: 'application/json',
        success: function(response) {
            console.log(response);
        },
        error: function(xhr, status, error) {
            console.error("Error activating host:", error);
        }
    });
}




function grabHost(hostId, macAddress, ipAddress) {
    var grabButton = $('#hostList li[data-key="' + hostId + '"] .grabButton');
    
    // Check if the button is currently active
    var isActive = grabButton.hasClass('active');
    
    // Send request to toggle grabbing
    $.ajax({
        type: 'POST',
        url: isActive ? '/stop_grab_host' : '/grab_host',
        data: JSON.stringify({ 
            host_id: hostId,
            mac_address: macAddress,
            ip_address: ipAddress
        }),
        contentType: 'application/json',
        success: function(response) {
            console.log('Toggle grabbing:', response);
        },
        error: function(xhr, status, error) {
            console.error('Error toggling grabbing:', error);
            // Handle error
        }
    });
}


function killHost(hostId, macAddress, ipAddress) {
    var killButton = $('<button class="killButton">Kill</button>').appendTo(listItem);

    var isActive = killButton.hasClass('active');
    // Voer de logica uit om de host te 'killen'
    $.ajax({
        type: 'POST',
        url: isActive ? '/stop_kill_host' : '/kill_host',
        data: JSON.stringify({ 
            host_id: hostId,
            mac_address: macAddress,
            ip_address: ipAddress
        }),
        contentType: 'application/json',
        success: function(response) {
            console.log('Host killed:', response);
            // Voer eventuele extra logica uit na het 'killen' van de host
        },
        error: function(xhr, status, error) {
            console.error('Error killing host:', error);
            // Voer eventuele foutafhandeling uit
        }
    });
}


// Function to remove deleted hosts
function removeDeletedHosts(response) {
    $('#hostList li').each(function() {
        var key = $(this).data('key');
        if (!(key in response)) {
            $(this).remove();
        }
    });
}



function fetchApplications() {
    if (snifferActive) {
        $.ajax({
            type: 'GET',
            url: '/send_host_information_dict',
            success: function(response) {
                $('#applicationList').empty();
                var skipDisplayMacAddresses = response.skip_display_mac_address;
                $.each(response.host_information, function(key, appInfo) {
                    var macAddress = appInfo.mac_address;
                    var websiteOrApp = appInfo.website_or_application_or_app;
                    var timesVisited = appInfo.times_visited;
                    var iconUrl = appInfo.icon_url;

                    if (skipDisplayMacAddresses.includes(macAddress)) {
                        return; // Skip this data entry
                    }

                    var card = $('<div class="card"></div>').appendTo('#applicationList');
                    if (iconUrl) {
                        var cardImg = $('<img class="card-img-top">').attr('src', iconUrl).attr('alt', 'Website Icon').appendTo(card);
                    }
                    var cardBody = $('<div class="card-body"></div>').appendTo(card);
                    
                    $('<p class="card-text"><b>MAC Address:</b> ' + macAddress + '</p>').appendTo(cardBody);
                    $('<p class="card-text"><b>Website or App:</b> ' + websiteOrApp + '</p>').appendTo(cardBody);
                    $('<p class="card-text"><b>Times Requested:</b> ' + timesVisited + '</p>').appendTo(cardBody);
                });
            },
            error: function(xhr, status, error) {
                console.error("Error fetching applications:", error);
            }
        });
    }
}
