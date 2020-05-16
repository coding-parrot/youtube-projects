package main

import (
	"fmt"
)

func main() {
	var ad AppDetails = AppDetails{}
	var ud UserDetails = UserDetails{}
	var androidDetails DeviceDetails = DeviceDetails{}
	androidDetails["Hyderabad"] = 20
	androidDetails["Mumbai"] = 12
	androidDetails["Chennai"] = 35
	var macDetails DeviceDetails = DeviceDetails{}
	macDetails["Delhi"] = 30
	macDetails["Mumbai"] = 10
	macDetails["Hyderabad"] = 17
	ud["android"] = androidDetails
	ud["mac"] = macDetails
	ad["gaurav.sen"] = ud
	fmt.Println(Transform(&ad))

	unknownDeviceDetails := DeviceDetails{}
	unknownDeviceDetails["Hyderabad"] = 90
	unknownDeviceDetails[""] = 12
	unknownUserDetails := UserDetails{}
	unknownUserDetails[""] = unknownDeviceDetails
	ad[""] = unknownUserDetails
	param := make(map[string]interface{})
	for k, v := range ad {
		param[k] = v
	}
	fmt.Println(GraphSearch(param, 0))
}

//Transform populates a map iteratively
func Transform(co *AppDetails) map[string]map[string]map[string]int {
	result := make(map[string]map[string]map[string]int)
	for username, userDetails := range *co {
		if username == "" {
			username = "John Doe"
		}
		result[username] = make(map[string]map[string]int)
		for device, deviceDetails := range userDetails {
			if device == "" {
				device = "Unknown"
			}
			result[username][device] = make(map[string]int)
			for location, timeUsed := range deviceDetails {
				if location == "" {
					location = "Unknown"
				}
				if timeUsed > 10 {
					result[username][device][location] = timeUsed
				}
			}
		}
	}
	return result
}

var keys = []string{"username", "device", "location"}

// GraphSearch populates a map recursively
func GraphSearch(dataSlice map[string]interface{}, level int) map[string]interface{} {
	result := make(map[string]interface{})
	if level == len(keys)-1 {
		for baseAttributeKey, baseAttributeValue := range dataSlice {
			result[baseAttributeKey], _ = baseAttributeValue.(int)
		}
	} else {
		for attributeKey, details := range dataSlice {
			attributeDetails := details.(map[string]interface{})
			result[attributeKey] = GraphSearch(attributeDetails, level+1)
		}
	}
	return result
}

//AppDetails stores the application details, for every userId
type AppDetails map[string]UserDetails

//UserDetails stores the device details of this user, for every deviceId
type UserDetails map[string]DeviceDetails

//DeviceDetails stores the timeUsed on this device, for every location
type DeviceDetails map[string]int
