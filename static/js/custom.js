let autocomplete;

function initAutoComplete() {
  autocomplete = new google.maps.places.Autocomplete(
    document.getElementById("id_address"),
    {
      types: ["geocode", "establishment"],
      //default in this app is Kenya only
      componentRestrictions: { country: "ke" },
    }
  );
  // function to specify what should happen when the prediction is clicked
  autocomplete.addListener("place_changed", onPlaceChanged);
}

function onPlaceChanged() {
  let place = autocomplete.getPlace();

  // User did not select the prediction. Reset the input field or alert()
  if (!place.geometry) {
    document.getElementById("id_address").placeholder = "Start typing...";
  } else {
    // console.log('place name=>', place.name)
  }

  // get the address components and assign them to the fields
  // console.log(place);
  let geocoder = new google.maps.Geocoder();
  let address = document.getElementById("id_address").value;

  geocoder.geocode({ address: address }, function (results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
      let latitude = results[0].geometry.location.lat();
      let longitude = results[0].geometry.location.lng();

      // console.log('lat=>', latitude);
      // console.log('long=>', longitude);
      $("#id_latitude").val(latitude);
      $("#id_longitude").val(longitude);

      $("#id_address").val(address);
    }
  });

  // loop through the address components and assign other address data
  console.log(place.address_components);
  for (let i = 0; i < place.address_components.length; i++) {
    for (let j = 0; j < place.address_components[i].types.length; j++) {
      // get country
      if (place.address_components[i].types[j] == "country") {
        $("#id_country").val(place.address_components[i].long_name);
      }
      // get county
      if (
        place.address_components[i].types[j] == "administrative_area_level_1"
      ) {
        $("#id_county").val(place.address_components[i].long_name);
      }
      // get city
      if (place.address_components[i].types[j] == "locality") {
        $("#id_city").val(place.address_components[i].long_name);
      }
      // get postal code
      if (place.address_components[i].types[j] == "postal_code") {
        $("#id_postal_code").val(place.address_components[i].long_name);
      } else {
        $("#id_postal_code").val("");
      }
    }
  }
}
