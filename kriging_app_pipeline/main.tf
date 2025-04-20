provider "azurerm" {
    features {}
}

resource "azurerm_resource_group" "rg" {
    name = "azure_devops_learning"
    location = "East US"
}

resource "azurerm_service_plan" "appserviceplan" {
    name                = "myAppServicePlan"
    location            = azurerm_resource_group.rg.location
    resource_group_name = azurerm_resource_group.rg.name
    os_type             = "Linux"
    sku_name            = "B1"
}